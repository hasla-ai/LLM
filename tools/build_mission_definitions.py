"""Forge H2 — 카탈로그에서 미션 정의 골격을 생성한다 (F-02).

정본 `docs/03-governance/mission-catalog.md` 에서 기계적으로 도출 가능한 필드만 채우고,
사람이 판단해야 하는 필드는 채우지 않고 표시만 남긴다.

도출 가능 (카탈로그가 직접 갖고 있음)
  mission_id · code · phase · owner_role · gate · output_contract.required_fields

규칙 도출 (규칙을 명시하고 근거를 extensions 에 남김, 확인 필요)
  risk_class · review_policy · executor

도출 불가 (자격자 작성 필요)
  purpose · dependencies 일부 · completion_criteria · block_conditions
  input_contract.required_fields 일부

카탈로그의 입력 칸은 약어다("Intent" 는 ProjectIntent 인지 NormalizedIntent 인지
카탈로그만으로 결정되지 않는다). 추측해서 채우면 미션 라우팅에 잘못된 선행관계가
들어가므로 모호한 것은 모호하다고 남긴다.

    python tools/build_mission_definitions.py          # 생성
    python tools/build_mission_definitions.py --report # 생성하지 않고 분석만
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "03-governance" / "mission-catalog.md"
SCHEMA = ROOT / "schemas" / "mission-definition.schema.json"
OUT = ROOT / "docs" / "03-governance" / "mission-definitions.draft.json"

TODO = "TODO-AUTHOR"
SCHEMA_VERSION = "1.0.0"

PHASE_RE = re.compile(r"^### Phase (\d+) — (.+)$")
MISSION_RE = re.compile(r"^M-\d{3}$")

# risk_class 규칙. 담당 역할에서 도출하며 확인 전에는 기준선이 아니다.
# A=행정, B=기술초안, C=전문가검토, D=고위험결정
RISK_RULES = [
    ("D", ("Sponsor", "Independent Reviewer")),
    ("C", ("HSE", "Regulatory", "Fire", "Process", "Electrical", "Grid", "Civil",
           "Structural", "Mechanical", "Piping", "ICSS", "Commissioning", "QA", "QC",
           "Chief Engineer", "Engineering", "Maintenance")),
    ("B", ("Construction", "EPC", "Procurement", "Operations", "Data", "AI")),
    ("A", ("PMO", "Product", "Commercial", "Finance", "Legal")),
]


def risk_class_for(owner: str) -> tuple[str, str]:
    for cls, keys in RISK_RULES:
        for key in keys:
            if key.lower() in owner.lower():
                return cls, f"담당 '{owner}' 의 '{key}' 로부터 규칙 도출"
    return "C", f"담당 '{owner}' 이 규칙에 없어 보수적으로 C"


def split_tokens(cell: str) -> list[str]:
    return [t.strip() for t in re.split(r"[·,/]", cell) if t.strip()]


def parse_catalog(path: Path) -> list[dict]:
    rows: list[dict] = []
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
            rows.append({
                "id": cells[0],
                "code": cells[1].strip("`"),
                "inputs": cells[2],
                "outputs": cells[3],
                "owner": cells[4],
                "gate": cells[5],
                "phase": phase,
            })
    return rows


def resolve_dependencies(rows: list[dict]) -> dict[str, dict]:
    """산출물→입력 사슬로 선행관계를 도출한다. 모호하면 확정하지 않는다."""
    produced: dict[str, str] = {}
    for row in rows:
        for token in split_tokens(row["outputs"]):
            produced[token] = row["id"]
    order = {row["id"]: i for i, row in enumerate(rows)}

    out: dict[str, dict] = {}
    for row in rows:
        resolved: list[str] = []
        ambiguous: list[dict] = []
        external: list[str] = []
        for token in split_tokens(row["inputs"]):
            if token in produced and produced[token] != row["id"]:
                dep = produced[token]
                if dep not in resolved:
                    resolved.append(dep)
                continue
            cands = sorted({
                mid for entity, mid in produced.items()
                if order[mid] < order[row["id"]]
                and (entity.endswith(token) or token in entity or entity in token)
            })
            if len(cands) == 1:
                if cands[0] not in resolved:
                    resolved.append(cands[0])
            elif len(cands) > 1:
                ambiguous.append({"input_token": token, "candidate_missions": cands})
            else:
                external.append(token)
        out[row["id"]] = {
            "resolved": sorted(resolved),
            "ambiguous": ambiguous,
            "external": external,
        }
    return out


def build(rows: list[dict], enum: list[str]) -> list[dict]:
    deps = resolve_dependencies(rows)
    defs: list[dict] = []
    for row in rows:
        dep = deps[row["id"]]
        risk, risk_basis = risk_class_for(row["owner"])
        needs_review = risk in ("C", "D")
        outputs = split_tokens(row["outputs"])

        defs.append({
            "mission_id": row["id"],
            "schema_version": SCHEMA_VERSION,
            "code": row["code"],
            "name": row["code"].replace("_", " "),
            "purpose": f"{TODO} — 카탈로그에 목적 문장이 없다. 자격자가 작성한다.",
            "phase": enum[row["phase"]],
            "owner_role": row["owner"],
            "risk_class": risk,
            "gate": row["gate"],
            "dependencies": dep["resolved"],
            "input_contract": {
                "schema_ref": f"{TODO} — 입력 스키마 미지정",
                "required_fields": split_tokens(row["inputs"]),
                "optional_fields": [],
                "accepts_unknowns": False,
            },
            "output_contract": {
                "schema_ref": f"{TODO} — 출력 스키마 미지정",
                "required_fields": outputs,
                "quality_checks": [f"{TODO} — 품질검사 조건 미작성"],
            },
            "completion_criteria": [f"{TODO} — 완료 판정기준 미작성"],
            "block_conditions": [f"{TODO} — 차단조건 미작성"],
            "review_policy": {
                "required": needs_review,
                "review_role": row["owner"],
                "approval_required_for_baseline": needs_review,
            },
            "executor": "hybrid",
            "implementation_ref": None,
            "extensions": {
                "source_of_truth": "docs/03-governance/mission-catalog.md",
                "catalog_phase_index": row["phase"],
                "generated_by": "tools/build_mission_definitions.py",
                "authoring_status": "draft_incomplete",
                "risk_class_basis": risk_basis,
                "risk_class_verified": False,
                "dependency_derivation": {
                    "resolved_from_io_chain": dep["resolved"],
                    "ambiguous_inputs": dep["ambiguous"],
                    "unresolved_inputs": dep["external"],
                },
            },
        })
    return defs


def main() -> int:
    rows = parse_catalog(CATALOG)
    enum = json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["phase"]["enum"]
    if len(rows) != 100:
        print(f"카탈로그에서 미션 {len(rows)}개를 읽었다. 100개가 아니다.")
        return 1

    defs = build(rows, enum)
    deps = resolve_dependencies(rows)

    n_amb = sum(len(d["ambiguous"]) for d in deps.values())
    n_ext = sum(len(d["external"]) for d in deps.values())
    n_res = sum(len(d["resolved"]) for d in deps.values())
    with_dep = sum(1 for d in deps.values() if d["resolved"])
    with_amb = sum(1 for d in deps.values() if d["ambiguous"])

    print("Forge H2 — 미션 정의 골격 생성 (F-02)")
    print("=" * 52)
    print(f"정본: {CATALOG.relative_to(ROOT).as_posix()}  미션 {len(rows)}개")
    print()
    print("[선행관계 도출]")
    print(f"  입력 사슬로 확정한 선행관계   {n_res:>3}건 ({with_dep}개 미션)")
    print(f"  모호해서 확정 못 한 입력      {n_amb:>3}건 ({with_amb}개 미션)")
    print(f"  산출 미션이 없는 외부 입력    {n_ext:>3}건")
    print()
    print("[자격자 작성이 필요한 필드]")
    for field, count in [
        ("purpose", len(defs)),
        ("completion_criteria", len(defs)),
        ("block_conditions", len(defs)),
        ("output_contract.quality_checks", len(defs)),
        ("input_contract.schema_ref", len(defs)),
        ("output_contract.schema_ref", len(defs)),
    ]:
        print(f"  {field:<32} {count:>3}/100")
    print()
    print("[규칙으로 제안한 필드 — 확인 필요]")
    dist: dict[str, int] = {}
    for d in defs:
        dist[d["risk_class"]] = dist.get(d["risk_class"], 0) + 1
    print(f"  risk_class 분포 {dict(sorted(dist.items()))}")
    print(f"  review_policy.required=true  {sum(1 for d in defs if d['review_policy']['required'])}/100")
    print()

    if "--report" in sys.argv:
        print("--report 모드. 파일을 쓰지 않았다.")
        return 0

    payload = {
        "schema_version": SCHEMA_VERSION,
        "title": "Forge H2 미션 정의 골격 (초안)",
        "source_of_truth": "docs/03-governance/mission-catalog.md",
        "item_schema": "schemas/mission-definition.schema.json",
        "authoring_status": "draft_incomplete",
        "warning": (
            "자동 생성된 골격이다. TODO-AUTHOR 가 남아 있는 항목은 미완성이며 "
            "기준선으로 승격하거나 미션 실행 근거로 사용하지 않는다."
        ),
        "generated_by": "tools/build_mission_definitions.py",
        "missions": defs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"생성: {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sys.exit(main())
