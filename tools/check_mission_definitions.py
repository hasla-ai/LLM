"""Forge H2 — 미션 정의 검사 (F-02).

두 가지를 따로 센다. 둘을 섞으면 골격이 완성본으로 오인된다.

1. 스키마 적합   `schemas/mission-definition.schema.json` 을 만족하는가
2. 내용 완결     TODO-AUTHOR 자리표시자가 남아 있지 않은가

스키마를 통과해도 자리표시자가 남아 있으면 미완성이다. 기준선으로 승격하지 않는다.
또한 정본(`mission-catalog.md`)과의 정합성(미션 100건·phase·gate·담당)을 함께 본다.

    python tools/check_mission_definitions.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFS = ROOT / "docs" / "03-governance" / "mission-definitions.draft.json"
SCHEMA = ROOT / "schemas" / "mission-definition.schema.json"
CATALOG = ROOT / "docs" / "03-governance" / "mission-catalog.md"

TODO = "TODO-AUTHOR"
PHASE_RE = re.compile(r"^### Phase (\d+) — (.+)$")
MISSION_RE = re.compile(r"^M-\d{3}$")


def parse_catalog(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    phase = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        matched = PHASE_RE.match(line)
        if matched:
            phase = int(matched.group(1))
            continue
        if phase is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 6 and MISSION_RE.match(cells[0]):
            rows[cells[0]] = {
                "code": cells[1].strip("`"),
                "owner": cells[4],
                "gate": cells[5],
                "phase": phase,
            }
    return rows


def find_todos(node, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(node, str):
        if TODO in node:
            hits.append(path)
    elif isinstance(node, dict):
        for k, v in node.items():
            hits += find_todos(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits += find_todos(v, f"{path}[{i}]")
    return hits


def main() -> int:
    if not DEFS.exists():
        print(f"파일 없음: {DEFS.relative_to(ROOT).as_posix()}")
        print("먼저 python tools/build_mission_definitions.py 를 실행한다.")
        return 1

    payload = json.loads(DEFS.read_text(encoding="utf-8"))
    missions = payload.get("missions", [])
    catalog = parse_catalog(CATALOG)
    errors: list[str] = []

    print("Forge H2 — 미션 정의 검사 (F-02)")
    print("=" * 52)
    print(f"대상: {DEFS.relative_to(ROOT).as_posix()}  미션 {len(missions)}개")
    print()

    # ---- 1. 스키마 적합 ----
    schema_ok = schema_fail = 0
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource

        registry = Registry()
        for path in SCHEMA.parent.glob("*.schema.json"):
            registry = registry.with_resource(
                path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8")))
            )
        validator = Draft202012Validator(
            json.loads(SCHEMA.read_text(encoding="utf-8")), registry=registry
        )
        for m in missions:
            errs = sorted(validator.iter_errors(m), key=lambda e: e.path)
            if errs:
                schema_fail += 1
                if schema_fail <= 5:
                    errors.append(f"스키마: {m.get('mission_id')} — {errs[0].message[:110]}")
            else:
                schema_ok += 1
        print(f"[스키마 적합] 통과 {schema_ok} · 실패 {schema_fail}")
    except ImportError:
        print("[스키마 적합] 건너뜀 — pip install jsonschema referencing")
        schema_ok = -1

    # ---- 2. 내용 완결 ----
    complete = 0
    field_counts: dict[str, int] = {}
    for m in missions:
        todos = find_todos(m)
        if not todos:
            complete += 1
        for t in todos:
            key = re.sub(r"\[\d+\]", "[]", t)
            field_counts[key] = field_counts.get(key, 0) + 1
    print(f"[내용 완결] 완결 {complete} · 미완성 {len(missions) - complete}")
    if field_counts:
        print("  자리표시자가 남은 필드:")
        for key, n in sorted(field_counts.items(), key=lambda kv: -kv[1]):
            print(f"    {key:<34} {n:>3}건")
    print()

    # ---- 3. 정본 정합성 ----
    enum = json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["phase"]["enum"]
    seen = set()
    for m in missions:
        mid = m.get("mission_id")
        seen.add(mid)
        cat = catalog.get(mid)
        if cat is None:
            errors.append(f"정합성: {mid} 이 카탈로그에 없다")
            continue
        if m.get("code") != cat["code"]:
            errors.append(f"정합성: {mid} code '{m.get('code')}' != 카탈로그 '{cat['code']}'")
        if m.get("gate") != cat["gate"]:
            errors.append(f"정합성: {mid} gate '{m.get('gate')}' != 카탈로그 '{cat['gate']}'")
        if m.get("owner_role") != cat["owner"]:
            errors.append(f"정합성: {mid} owner_role 이 카탈로그 담당과 다르다")
        if m.get("phase") != enum[cat["phase"]]:
            errors.append(f"정합성: {mid} phase '{m.get('phase')}' != '{enum[cat['phase']]}'")
        for dep in m.get("dependencies", []):
            if dep not in catalog:
                errors.append(f"정합성: {mid} 의 선행 미션 '{dep}' 이 카탈로그에 없다")
    for mid in catalog:
        if mid not in seen:
            errors.append(f"정합성: 카탈로그의 {mid} 에 대한 정의가 없다")

    # 선행관계 순환 검사
    graph = {m["mission_id"]: list(m.get("dependencies", [])) for m in missions}
    state: dict[str, int] = {}

    def walk(node: str, stack: list[str]) -> None:
        if state.get(node) == 2:
            return
        if state.get(node) == 1:
            errors.append(f"선행관계: 순환 {' -> '.join(stack[stack.index(node):] + [node])}")
            return
        state[node] = 1
        for nxt in graph.get(node, []):
            if nxt in graph:
                walk(nxt, stack + [node])
        state[node] = 2

    for node in graph:
        walk(node, [])

    print(f"[정본 정합성] 불일치 {len([e for e in errors if e.startswith(('정합성', '선행관계'))])}건")
    print()

    # ---- 결과 ----
    print("=" * 52)
    if errors:
        for e in errors[:20]:
            print(f"  FAIL  {e}")
        if len(errors) > 20:
            print(f"  ... 외 {len(errors) - 20}건")
        print()
        print("결과: 실패")
        return 1

    status = payload.get("authoring_status")
    print(f"스키마 {schema_ok}/{len(missions)} · 내용완결 {complete}/{len(missions)} · 불일치 0")
    if complete < len(missions):
        print(f"결과: 통과 (골격) — authoring_status={status}")
        print()
        print(f"주의: {len(missions) - complete}개 미션이 미완성이다. TODO-AUTHOR 가 남은 항목은")
        print("기준선으로 승격하거나 미션 실행 근거로 사용하지 않는다 (F-02 미해소).")
    else:
        print("결과: 통과 — 전건 완결")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sys.exit(main())
