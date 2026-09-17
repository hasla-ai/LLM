"""JSON-first, auditable knowledge catalog and retrieval index for Forge H2.

Knowledge is authored and materialized as JSON. SQLite is retained only as a
derived lexical-search index and never becomes the source of truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG = ROOT / "catalog.json"
LEGACY_JSONL = ROOT / "entries.jsonl"
DEFAULT_DB = ROOT / "knowledge.sqlite3"
AGENT_DB_DIR = ROOT / "agent-databases"
OFFLINE_REGISTER = ROOT / "offline-source-register.json"
OFFLINE_BUNDLE_DIR = ROOT / "offline-bundle"
AGENT_REGISTRY = ROOT.parent / "agents" / "registry.json"
INTERNATIONAL_OVERLAY = ROOT.parent / "agents" / "international-overlay.json"
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[가-힣]+")
AUTHORITY_SCORE = {
    "T0_official_law_or_permit": 5.0,
    "T1_official_standard_or_authority": 4.0,
    "T2_certified_test_or_engineer": 3.0,
    "T3_vendor_or_contract": 2.0,
    "T4_internal_lesson_or_ai_draft": 1.0,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_source_register() -> dict[str, Any]:
    return json.loads(OFFLINE_REGISTER.read_text(encoding="utf-8"))


def _offline_source_status(knowledge_id: str) -> dict[str, Any]:
    register = _load_source_register()
    record = next((item for item in register.get("sources", []) if item.get("knowledge_id") == knowledge_id), None)
    if not record:
        return {"status": "missing_register", "local_artifact": None, "required_for_baseline": True}
    result = {
        "status": record.get("status", "missing_local"),
        "local_artifact": record.get("local_artifact"),
        "required_for_baseline": bool(record.get("required_for_baseline")),
    }
    if record.get("status") == "available_local":
        artifact = record.get("local_artifact")
        path = ROOT.parent / artifact if artifact else None
        if not path or not path.exists():
            result["status"] = "missing_local"
        elif record.get("sha256") and _sha256_path(path) != record["sha256"]:
            result["status"] = "integrity_mismatch"
    return result


def offline_check() -> dict[str, Any]:
    """Check whether the local project can work offline without remote fetches."""

    catalog = json.loads(DEFAULT_CATALOG.read_text(encoding="utf-8"))
    register = _load_source_register()
    catalog_ids = {entry["knowledge_id"] for entry in catalog.get("entries", [])}
    register_ids = {item["knowledge_id"] for item in register.get("sources", [])}
    statuses = {knowledge_id: _offline_source_status(knowledge_id) for knowledge_id in sorted(catalog_ids)}
    missing_required = [knowledge_id for knowledge_id, item in statuses.items() if item["required_for_baseline"] and item["status"] != "available_local"]
    missing_register = sorted(catalog_ids - register_ids)
    return {
        "mode": "offline",
        "network_policy": "deny_all_remote_fetch",
        "catalog_entries": len(catalog_ids),
        "source_register_entries": len(register_ids),
        "available_local": sum(item["status"] == "available_local" for item in statuses.values()),
        "metadata_only": sum(item["status"] == "metadata_only" for item in statuses.values()),
        "missing_local": sum(item["status"] in {"missing_local", "integrity_mismatch", "missing_register"} for item in statuses.values()),
        "missing_register": missing_register,
        "missing_required_sources": missing_required,
        "baseline_ready": not missing_required and not missing_register,
        "source_status": statuses,
        "warnings": ["Remote source text is never fetched in offline mode.", "A metadata-only or missing local source blocks baseline promotion."] if missing_required else [],
    }


def build_offline_bundle(output_dir: str | Path = OFFLINE_BUNDLE_DIR) -> dict[str, Any]:
    """Create a portable JSON bundle with hashes and no network dependency."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    register = _load_source_register()
    copy_map = {
        "catalog.json": DEFAULT_CATALOG,
        "formula-library.json": ROOT / "formula-library.json",
        "professional-foundations.json": ROOT / "professional-foundations.json",
        "access-policy.json": ROOT / "access-policy.json",
        "registry.json": ROOT / "registry.json",
        "agent-databases/manifest.json": AGENT_DB_DIR / "manifest.json",
        "source-cache/README.md": ROOT / "source-cache" / "README.md",
    }
    for schema in (ROOT.parent / "schemas").glob("*.schema.json"):
        copy_map[f"schemas/{schema.name}"] = schema
    for agent in json.loads((AGENT_DB_DIR / "manifest.json").read_text(encoding="utf-8"))["agents"]:
        relative = agent["database"]
        copy_map[relative] = ROOT.parent / relative

    cache_root = output / "source-cache"
    cache_root.mkdir(parents=True, exist_ok=True)
    bundled_sources = []
    for item in register.get("sources", []):
        copied = dict(item)
        if item.get("status") == "available_local" and item.get("local_artifact"):
            source_path = ROOT.parent / item["local_artifact"]
            if source_path.exists():
                target_name = item["knowledge_id"] + source_path.suffix
                target = cache_root / target_name
                shutil.copy2(source_path, target)
                copied["local_artifact"] = f"source-cache/{target_name}"
                copied["sha256"] = _sha256_path(target)
        bundled_sources.append(copied)
    bundled_register = dict(register)
    bundled_register["sources"] = bundled_sources
    register_target = output / "offline-source-register.json"
    register_target.write_text(json.dumps(bundled_register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    copy_map["offline-source-register.json"] = register_target
    copy_map["offline-requirements.json"] = ROOT / "offline-requirements.json"

    files = []
    for relative, source in copy_map.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        files.append({"path": relative.replace("\\", "/"), "sha256": _sha256_path(target), "bytes": target.stat().st_size})
    files.sort(key=lambda item: item["path"])
    manifest = {
        "$schema": "https://forge-h2.local/schema/offline-bundle-manifest.schema.json",
        "project_id": "FHZ-ENTERPRISE-001",
        "bundle_version": "1.0.0",
        "network_policy": "deny_all_remote_fetch",
        "created_at": now_utc(),
        "files": files,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"bundle": str(output), "files": len(files), "network_policy": manifest["network_policy"]}


def connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    return db


def init_db(db_path: str | Path = DEFAULT_DB) -> None:
    db = connect(db_path)
    try:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                knowledge_id TEXT NOT NULL,
                revision TEXT NOT NULL,
                title TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                domains_json TEXT NOT NULL,
                jurisdictions_json TEXT NOT NULL,
                languages_json TEXT NOT NULL,
                authority_level TEXT NOT NULL,
                source_json TEXT NOT NULL,
                status TEXT NOT NULL,
                applies_to_json TEXT NOT NULL,
                content_json TEXT NOT NULL,
                verification_json TEXT NOT NULL,
                access_policy_json TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                raw_json TEXT NOT NULL,
                ingested_at TEXT NOT NULL,
                PRIMARY KEY (knowledge_id, revision)
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_status ON knowledge_entries(status);
            CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_entries(knowledge_type);
            CREATE INDEX IF NOT EXISTS idx_knowledge_authority ON knowledge_entries(authority_level);
            """
        )
        db.commit()
    finally:
        db.close()


def _required(entry: dict[str, Any], fields: Iterable[str]) -> None:
    missing = [field for field in fields if field not in entry]
    if missing:
        raise ValueError(f"knowledge entry missing fields: {', '.join(missing)}")


def _validate_entry(entry: dict[str, Any]) -> None:
    _required(
        entry,
        [
            "knowledge_id",
            "title",
            "knowledge_type",
            "domains",
            "jurisdictions",
            "languages",
            "authority_level",
            "source",
            "revision",
            "status",
            "applies_to",
            "content",
            "verification",
            "access_policy",
        ],
    )
    if not str(entry["knowledge_id"]).startswith("KNW-"):
        raise ValueError("knowledge_id must start with KNW-")
    if entry["status"] not in {"draft", "active", "superseded", "withdrawn", "pending_verification"}:
        raise ValueError(f"unsupported status: {entry['status']}")
    if entry["verification"]["status"] == "authority_confirmed" and entry["authority_level"] not in {
        "T0_official_law_or_permit",
        "T1_official_standard_or_authority",
    }:
        raise ValueError("authority_confirmed is reserved for official law, permits or standards")
    source = entry["source"]
    evidence_ids = entry["verification"].get("evidence_ids", [])
    if not source.get("url") and not source.get("locator") and not evidence_ids:
        raise ValueError("knowledge entry must have a source URL, locator, or Evidence ID")


def _read_entries(entries_path: str | Path) -> list[dict[str, Any]]:
    path = Path(entries_path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
        return payload["entries"]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("JSON knowledge source must be an object with entries or an array")


def export_catalog(entries_path: str | Path = LEGACY_JSONL, catalog_path: str | Path = DEFAULT_CATALOG) -> dict[str, Any]:
    entries = _read_entries(entries_path)
    for entry in entries:
        _validate_entry(entry)
    payload = {
        "$schema": "https://forge-h2.local/schema/knowledge-catalog.schema.json",
        "project_id": "FHZ-ENTERPRISE-001",
        "catalog_version": "1.0.0",
        "source_of_truth": "knowledge/catalog.json",
        "generated_at": now_utc(),
        "entries": entries,
    }
    output = Path(catalog_path)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"entries": len(entries), "catalog": str(output)}


def ingest_jsonl(entries_path: str | Path, db_path: str | Path = DEFAULT_DB) -> dict[str, int]:
    """Ingest JSON or legacy JSONL into the derived SQLite search index."""
    init_db(db_path)
    inserted = 0
    skipped = 0
    db = connect(db_path)
    try:
        entries = _read_entries(entries_path)
        for line_number, entry in enumerate(entries, start=1):
            try:
                _validate_entry(entry)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid entry at line {line_number}: {exc}") from exc
            raw = json.dumps(entry, ensure_ascii=False, sort_keys=True)
            content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            result = db.execute(
                """
                INSERT OR IGNORE INTO knowledge_entries (
                    knowledge_id, revision, title, knowledge_type, domains_json,
                    jurisdictions_json, languages_json, authority_level, source_json,
                    status, applies_to_json, content_json, verification_json,
                    access_policy_json, content_hash, raw_json, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["knowledge_id"],
                    entry["revision"],
                    entry["title"],
                    entry["knowledge_type"],
                    json.dumps(entry["domains"], ensure_ascii=False),
                    json.dumps(entry["jurisdictions"], ensure_ascii=False),
                    json.dumps(entry["languages"], ensure_ascii=False),
                    entry["authority_level"],
                    json.dumps(entry["source"], ensure_ascii=False),
                    entry["status"],
                    json.dumps(entry["applies_to"], ensure_ascii=False),
                    json.dumps(entry["content"], ensure_ascii=False),
                    json.dumps(entry["verification"], ensure_ascii=False),
                    json.dumps(entry["access_policy"], ensure_ascii=False),
                    content_hash,
                    raw,
                    now_utc(),
                ),
            )
            if result.rowcount:
                inserted += 1
            else:
                skipped += 1
        db.commit()
    finally:
        db.close()
    return {"inserted": inserted, "skipped": skipped}


def _agent_ids() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for registry_path in (AGENT_REGISTRY, INTERNATIONAL_OVERLAY):
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        key = "agents" if registry_path.name == "registry.json" else "international_agents"
        records.extend(payload.get(key, []))
    unique: dict[str, dict[str, Any]] = {}
    for record in records:
        unique[record["agent_id"]] = record
    return list(unique.values())


def _load_rows(db_path: str | Path) -> list[sqlite3.Row]:
    db = connect(db_path)
    try:
        return db.execute("SELECT * FROM knowledge_entries WHERE status = 'active'").fetchall()
    finally:
        db.close()


def _copy_entry(db: sqlite3.Connection, row: sqlite3.Row) -> None:
    db.execute(
        """
        INSERT OR IGNORE INTO knowledge_entries (
            knowledge_id, revision, title, knowledge_type, domains_json,
            jurisdictions_json, languages_json, authority_level, source_json,
            status, applies_to_json, content_json, verification_json,
            access_policy_json, content_hash, raw_json, ingested_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tuple(row[field] for field in (
            "knowledge_id", "revision", "title", "knowledge_type", "domains_json",
            "jurisdictions_json", "languages_json", "authority_level", "source_json",
            "status", "applies_to_json", "content_json", "verification_json",
            "access_policy_json", "content_hash", "raw_json", "ingested_at",
        )),
    )


def _active_catalog_entries(catalog_path: str | Path = DEFAULT_CATALOG) -> list[dict[str, Any]]:
    path = Path(catalog_path)
    if path.exists():
        return [entry for entry in _read_entries(path) if entry.get("status") == "active"]
    return [json.loads(row["raw_json"]) for row in _load_rows(DEFAULT_DB)]


def build_agent_databases(
    *,
    db_path: str | Path = DEFAULT_DB,
    output_dir: str | Path = AGENT_DB_DIR,
) -> dict[str, Any]:
    """Materialize one read-enabled, source-preserving DB per registered Agent."""

    # Keep the derived search index synchronized with the canonical JSON
    # catalog before materializing Agent-specific views.
    if DEFAULT_CATALOG.exists():
        ingest_jsonl(DEFAULT_CATALOG, db_path)
    init_db(db_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    central_rows = _load_rows(db_path)
    central_entries = _active_catalog_entries()
    agents = _agent_ids()
    manifest_agents: list[dict[str, Any]] = []
    for agent in agents:
        agent_id = agent["agent_id"]
        agent_roles = {agent.get("pm_role"), agent.get("name")}
        agent_roles.discard(None)
        agent_db_path = output / f"{agent_id}.sqlite3"
        init_db(agent_db_path)
        scoped = []
        for row in central_rows:
            applies = json.loads(row["applies_to_json"])
            allowed_ids = set(applies.get("agent_ids", []))
            allowed_roles = set(applies.get("roles", []))
            if "*" in allowed_ids or agent_id in allowed_ids or agent_roles.intersection(allowed_roles):
                scoped.append(row)
        scoped_entries = []
        for entry in central_entries:
            applies = entry.get("applies_to", {})
            allowed_ids = set(applies.get("agent_ids", []))
            allowed_roles = set(applies.get("roles", []))
            if "*" in allowed_ids or agent_id in allowed_ids or agent_roles.intersection(allowed_roles):
                scoped_entries.append(entry)

        agent_json_path = output / f"{agent_id}.json"
        agent_json_path.write_text(
            json.dumps(
                {
                    "$schema": "https://forge-h2.local/schema/agent-knowledge-database.schema.json",
                    "project_id": "FHZ-ENTERPRISE-001",
                    "agent_id": agent_id,
                    "database_kind": "professional_knowledge",
                    "source_of_truth": "knowledge/catalog.json",
                    "generated_at": now_utc(),
                    "entries": scoped_entries,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        agent_db = connect(agent_db_path)
        try:
            # Agent DBs are materialized views of the central Source Catalog.
            # Rebuild from the current active snapshot so withdrawn or
            # superseded central entries cannot remain readable in a stale DB.
            agent_db.execute("DELETE FROM knowledge_entries")
            for row in scoped:
                _copy_entry(agent_db, row)
            agent_db.commit()
        finally:
            agent_db.close()
        manifest_agents.append({
            "agent_id": agent_id,
            "database": str(agent_json_path.relative_to(ROOT.parent)).replace("\\", "/"),
            "index_database": str(agent_db_path.relative_to(ROOT.parent)).replace("\\", "/"),
            "entry_count": len(scoped),
            "access": "read",
            "source_of_truth": "knowledge/catalog.json",
        })
    manifest = {
        "project_id": "FHZ-ENTERPRISE-001",
        "generated_at": now_utc(),
        "central_source_catalog": "knowledge/catalog.json",
        "derived_search_index": "knowledge/knowledge.sqlite3",
        "cross_agent_access": "read",
        "agents": manifest_agents,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"agent_databases": len(manifest_agents), "source_entries": len(central_rows), "manifest": str(output / "manifest.json")}


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(value) if len(token) > 1}


def search_formulas(query: str, *, top_k: int = 10, library_path: str | Path = ROOT / "formula-library.json") -> dict[str, Any]:
    """Search the JSON formula library without executing any expression."""

    requested = _tokens(query)
    payload = json.loads(Path(library_path).read_text(encoding="utf-8"))
    ranked: list[tuple[float, dict[str, Any], set[str]]] = []
    for formula in payload.get("formulas", []):
        searchable = " ".join([
            formula["formula_id"], formula["domain"], formula["name"],
            formula["equation_ascii"], formula.get("sympy", ""),
            " ".join(item["meaning"] for item in formula["variables"]),
        ])
        overlap = requested.intersection(_tokens(searchable))
        if overlap:
            ranked.append((float(len(overlap)), formula, overlap))
    ranked.sort(key=lambda item: (-item[0], item[1]["formula_id"]))
    hits = []
    for rank, (score, formula, overlap) in enumerate(ranked[: max(1, min(top_k, 50))], start=1):
        hits.append({
            "rank": rank,
            "formula_id": formula["formula_id"],
            "name": formula["name"],
            "domain": formula["domain"],
            "equation_latex": formula["equation_latex"],
            "equation_ascii": formula["equation_ascii"],
            "python": formula["python"],
            "variables": formula["variables"],
            "assumptions": formula["assumptions"],
            "source_knowledge_id": formula["source_knowledge_id"],
            "verification_status": formula["verification_status"],
            "relevance": {"score": score, "matched_tokens": sorted(overlap)},
        })
    return {
        "query": query,
        "library": "knowledge/formula-library.json",
        "execution_policy": payload["execution_policy"],
        "hits": hits,
        "warnings": [] if hits else ["no formula matched; do not invent or execute an unregistered formula"],
    }


def _json(row: sqlite3.Row, field: str) -> Any:
    return json.loads(row[field])


def retrieve(
    query: str,
    *,
    request_id: str | None = None,
    requesting_agent_id: str | None = None,
    source_agent_ids: list[str] | None = None,
    phase: str | None = None,
    jurisdiction: str | None = None,
    domains: list[str] | None = None,
    knowledge_types: list[str] | None = None,
    top_k: int = 5,
    offline: bool = False,
    db_path: str | Path = DEFAULT_DB,
) -> dict[str, Any]:
    """Retrieve active knowledge with deterministic score and provenance."""

    init_db(db_path)
    request_id = request_id or f"RET-AUTO-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    requested = _tokens(query)
    if not requested:
        return {"request_id": request_id, "generated_at": now_utc(), "hits": [], "warnings": ["query has no searchable tokens"], "extensions": {}}

    clauses = ["status = 'active'"]
    params: list[Any] = []
    if knowledge_types:
        clauses.append("knowledge_type IN (%s)" % ",".join("?" for _ in knowledge_types))
        params.extend(knowledge_types)
    source_ids = []
    for agent_id in [requesting_agent_id, *(source_agent_ids or [])]:
        if agent_id and agent_id not in source_ids:
            source_ids.append(agent_id)
    rows_by_key: dict[tuple[str, str], sqlite3.Row] = {}
    for agent_id in source_ids:
        agent_path = AGENT_DB_DIR / f"{agent_id}.sqlite3"
        if agent_path.exists():
            for row in _load_rows(agent_path):
                rows_by_key[(row["knowledge_id"], row["revision"])] = row
    db = connect(db_path)
    try:
        for row in db.execute(
            "SELECT * FROM knowledge_entries WHERE " + " AND ".join(clauses),
            params,
        ).fetchall():
            rows_by_key.setdefault((row["knowledge_id"], row["revision"]), row)
    finally:
        db.close()
    rows = list(rows_by_key.values())
    scope_ids = set(source_ids or ([requesting_agent_id] if requesting_agent_id else []))

    domain_filter = {x.lower() for x in (domains or [])}
    ranked: list[tuple[float, sqlite3.Row, list[str]]] = []
    for row in rows:
        row_domains = {x.lower() for x in _json(row, "domains_json")}
        if domain_filter and not domain_filter.intersection(row_domains):
            continue
        applies = _json(row, "applies_to_json")
        if phase and phase not in applies.get("phases", []):
            continue
        row_jurisdictions = {x.lower() for x in _json(row, "jurisdictions_json")}
        if jurisdiction and jurisdiction.lower() not in row_jurisdictions and "international" not in row_jurisdictions and "global" not in row_jurisdictions:
            continue
        if scope_ids and applies.get("agent_ids") and not scope_ids.intersection(applies["agent_ids"]) and "*" not in applies["agent_ids"]:
            continue

        content = _json(row, "content_json")
        searchable = " ".join([row["title"], " ".join(_json(row, "domains_json")), content["summary"], " ".join(content.get("keywords", [])), " ".join(c["statement"] for c in content["claims"])])
        searchable_tokens = _tokens(searchable)
        overlap = requested.intersection(searchable_tokens)
        if not overlap:
            continue
        score = len(overlap) * 2.0 + AUTHORITY_SCORE.get(row["authority_level"], 0.0)
        reasons = [f"query_overlap:{','.join(sorted(overlap))}", f"authority:{row['authority_level']}"]
        if requesting_agent_id and requesting_agent_id in applies.get("agent_ids", []):
            score += 3.0
            reasons.append("agent_scope_match")
        elif source_ids and any(agent_id in applies.get("agent_ids", []) for agent_id in source_ids):
            score += 1.5
            reasons.append("cross_agent_scope_match")
        if phase and phase in applies.get("phases", []):
            score += 2.0
            reasons.append("phase_scope_match")
        if jurisdiction and jurisdiction.lower() in row_jurisdictions:
            score += 2.0
            reasons.append("jurisdiction_match")
        if _json(row, "verification_json").get("status") in {"expert_verified", "authority_confirmed"}:
            score += 2.0
            reasons.append("verified")
        ranked.append((score, row, reasons))

    ranked.sort(key=lambda item: (-item[0], -AUTHORITY_SCORE.get(item[1]["authority_level"], 0.0), item[1]["knowledge_id"]))
    hits = []
    offline_blocked: list[str] = []
    for rank, (score, row, reasons) in enumerate(ranked[: max(1, min(top_k, 50))], start=1):
        source = _json(row, "source_json")
        content = _json(row, "content_json")
        verification = _json(row, "verification_json")
        offline_status = "not_requested"
        local_artifact = None
        if offline:
            offline_info = _offline_source_status(row["knowledge_id"])
            offline_status = offline_info["status"]
            local_artifact = offline_info.get("local_artifact")
            if offline_info["required_for_baseline"] and offline_status != "available_local":
                offline_blocked.append(row["knowledge_id"])
        hits.append({
            "rank": rank,
            "knowledge_id": row["knowledge_id"],
            "title": row["title"],
            "score": round(score, 3),
            "summary": content["summary"],
            "source": {
                "source_kind": source.get("source_kind"),
                "publisher": source["publisher"],
                "url": source["url"],
                "locator": source.get("locator"),
                "evidence_ids": verification.get("evidence_ids", []),
                "local_artifact": local_artifact,
                "offline_status": offline_status,
            },
            "revision": row["revision"],
            "verification_status": verification["status"],
            "relevance_reasons": reasons,
        })
    warnings = [] if hits else ["no active verified knowledge matched; do not infer a decision"]
    if offline and offline_blocked:
        warnings.append("offline mode: local source artifact is missing; baseline promotion is blocked")
    return {
        "request_id": request_id,
        "generated_at": now_utc(),
        "hits": hits,
        "warnings": warnings,
        "extensions": {"retrieval_mode": "deterministic_lexical", "offline": offline, "offline_blocked_knowledge_ids": sorted(set(offline_blocked))},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Forge H2 knowledge database")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    export_parser = sub.add_parser("export-json")
    export_parser.add_argument("entries", nargs="?", default=str(LEGACY_JSONL))
    export_parser.add_argument("--output", default=str(DEFAULT_CATALOG))
    ingest_parser = sub.add_parser("ingest")
    ingest_parser.add_argument("entries", nargs="?")
    sub.add_parser("build-agent-databases")
    search_parser = sub.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--agent-id")
    search_parser.add_argument("--phase")
    search_parser.add_argument("--jurisdiction")
    search_parser.add_argument("--domain", action="append", dest="domains")
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--offline", action="store_true", help="deny remote fetch and report missing local source artifacts")
    formula_parser = sub.add_parser("search-formulas")
    formula_parser.add_argument("query")
    formula_parser.add_argument("--top-k", type=int, default=10)
    offline_check_parser = sub.add_parser("offline-check")
    offline_bundle_parser = sub.add_parser("build-offline-bundle")
    offline_bundle_parser.add_argument("--output", default=str(OFFLINE_BUNDLE_DIR))
    args = parser.parse_args()

    if args.command == "init":
        init_db()
        print(json.dumps({"status": "initialized", "database": str(DEFAULT_DB)}, ensure_ascii=False))
    elif args.command == "export-json":
        print(json.dumps(export_catalog(args.entries, args.output), ensure_ascii=False))
    elif args.command == "ingest":
        source = args.entries or (str(DEFAULT_CATALOG) if DEFAULT_CATALOG.exists() else str(LEGACY_JSONL))
        print(json.dumps(ingest_jsonl(source), ensure_ascii=False))
    elif args.command == "build-agent-databases":
        print(json.dumps(build_agent_databases(), ensure_ascii=False))
    elif args.command == "search":
        print(json.dumps(retrieve(args.query, requesting_agent_id=args.agent_id, phase=args.phase, jurisdiction=args.jurisdiction, domains=args.domains, top_k=args.top_k, offline=args.offline), ensure_ascii=False, indent=2))
    elif args.command == "search-formulas":
        print(json.dumps(search_formulas(args.query, top_k=args.top_k), ensure_ascii=False, indent=2))
    elif args.command == "offline-check":
        print(json.dumps(offline_check(), ensure_ascii=False, indent=2))
    elif args.command == "build-offline-bundle":
        print(json.dumps(build_offline_bundle(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
