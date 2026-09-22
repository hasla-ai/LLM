"""Forge H2 — 단계(phase) 분류 3파일 일치 검사 (F-01).

정본: docs/03-governance/mission-catalog.md
  - 단계 구분과 단계별 미션 배정, 미션별 Gate 를 정의한다.

종속:
  - schemas/mission-definition.schema.json  phase enum (이름·순서)
  - workflow/process-agent-map.json         단계별 미션 배정·Gate·Agent 라우팅

이 셋이 어긋나면 미션이 잘못된 전문가 Agent 에게 라우팅된다.
실패 시 종료코드 1.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "03-governance" / "mission-catalog.md"
SCHEMA = ROOT / "schemas" / "mission-definition.schema.json"
AGENT_MAP = ROOT / "workflow" / "process-agent-map.json"
REGISTRY = ROOT / "agents" / "registry.json"

MISSION_RE = re.compile(r"^M-\d{3}$")
PHASE_RE = re.compile(r"^### Phase (\d+) — (.+)$")
GATE_RE = re.compile(r"^G\d$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_catalog(path: Path):
    """정본 카탈로그에서 단계·미션·Gate 를 읽는다."""
    phases: "OrderedDict[int, dict]" = OrderedDict()
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        matched = PHASE_RE.match(line)
        if matched:
            idx = int(matched.group(1))
            if idx in phases:
                err(f"카탈로그: Phase {idx} 헤딩이 중복이다")
            current = idx
            phases[idx] = {"label_ko": matched.group(2).strip(), "missions": [], "gates": {}}
            continue
        if current is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or not MISSION_RE.match(cells[0]):
            continue
        mission_id, gate = cells[0], cells[5]
        if not GATE_RE.match(gate):
            err(f"카탈로그: {mission_id} 의 Gate 값 '{gate}' 이 G0~G9 형식이 아니다")
        phases[current]["missions"].append(mission_id)
        phases[current]["gates"][mission_id] = gate
    return phases


def check_catalog_integrity(phases) -> list[str]:
    """정본 자체가 성립하는지 먼저 본다."""
    all_missions = [m for p in phases.values() for m in p["missions"]]

    dupes = [m for m, n in Counter(all_missions).items() if n > 1]
    if dupes:
        err(f"카탈로그: 미션 ID 중복 {sorted(dupes)}")

    if list(phases) != list(range(len(phases))):
        err(f"카탈로그: Phase 번호가 0부터 연속이 아니다 — {list(phases)}")

    expected = [f"M-{i:03d}" for i in range(1, len(all_missions) + 1)]
    if sorted(all_missions) != expected:
        missing = sorted(set(expected) - set(all_missions))
        extra = sorted(set(all_missions) - set(expected))
        if missing:
            err(f"카탈로그: 미션 결번 {missing}")
        if extra:
            err(f"카탈로그: 범위 밖 미션 {extra}")

    for idx, p in phases.items():
        ordered = sorted(p["missions"])
        if p["missions"] != ordered:
            err(f"카탈로그: Phase {idx} 의 미션 순서가 정렬되어 있지 않다")
        nums = [int(m.split("-")[1]) for m in ordered]
        if nums and nums != list(range(nums[0], nums[0] + len(nums))):
            err(f"카탈로그: Phase {idx} 의 미션 번호가 연속 블록이 아니다 — {ordered[0]}~{ordered[-1]}")

    return all_missions


def main() -> int:
    for path in (CATALOG, SCHEMA, AGENT_MAP):
        if not path.exists():
            print(f"파일 없음: {path.relative_to(ROOT)}")
            return 1

    print("Forge H2 — 단계 분류 3파일 일치 검사 (F-01)")
    print("=" * 52)
    print(f"정본: {CATALOG.relative_to(ROOT).as_posix()}")
    print()

    # ---- 1. 정본 ----
    phases = parse_catalog(CATALOG)
    all_missions = check_catalog_integrity(phases)
    print(f"[정본] 단계 {len(phases)}개 · 미션 {len(all_missions)}개")
    for idx, p in phases.items():
        gates = sorted(set(p["gates"].values()))
        span = f'{p["missions"][0]}~{p["missions"][-1]}' if p["missions"] else "(없음)"
        print(f'  Phase {idx}  {p["label_ko"]:<24} {span}  gate={"/".join(gates)}')
    print()

    # ---- 2. 스키마 enum ----
    schema = load_json(SCHEMA)
    try:
        enum = schema["properties"]["phase"]["enum"]
    except KeyError:
        err("스키마: properties.phase.enum 이 없다")
        enum = []

    print(f"[스키마] phase enum {len(enum)}개")
    if len(enum) != len(phases):
        err(f"스키마: enum 개수 {len(enum)} 와 카탈로그 단계 수 {len(phases)} 가 다르다")
    if len(set(enum)) != len(enum):
        err(f"스키마: enum 에 중복 값이 있다 — {[v for v, n in Counter(enum).items() if n > 1]}")
    print(f"  {enum}")
    print()

    # ---- 3. workflow 맵 ----
    amap = load_json(AGENT_MAP)
    map_phases = amap.get("phases", [])
    print(f"[workflow 맵] 단계 {len(map_phases)}개  v{amap.get('version','?')}")

    if len(map_phases) != len(phases):
        err(f"맵: 단계 수 {len(map_phases)} 가 카탈로그 {len(phases)} 와 다르다")

    map_names = [p.get("name") for p in map_phases]
    if enum and map_names != enum[: len(map_names)]:
        err("맵: 단계 이름·순서가 스키마 enum 과 다르다")
        for i, (got, want) in enumerate(zip(map_names, enum)):
            if got != want:
                err(f"  위치 {i}: 맵='{got}' 스키마='{want}'")

    seen: Counter = Counter()
    for i, mp in enumerate(map_phases):
        name = mp.get("name", f"<{i}>")
        pid = mp.get("phase_id", "?")
        want_id = f"P{i + 1:02d}"
        if pid != want_id:
            err(f"맵: {name} 의 phase_id 가 '{pid}' 인데 순서상 '{want_id}' 여야 한다")

        if i not in phases:
            err(f"맵: {name} 에 대응하는 카탈로그 Phase {i} 가 없다")
            continue
        cat = phases[i]

        got_missions = list(mp.get("mission_ids", []))
        seen.update(got_missions)
        if got_missions != cat["missions"]:
            err(f"맵: {pid} {name} 의 미션 배정이 카탈로그 Phase {i} 와 다르다")
            only_map = sorted(set(got_missions) - set(cat["missions"]))
            only_cat = sorted(set(cat["missions"]) - set(got_missions))
            if only_map:
                err(f"  맵에만 있음: {only_map}")
            if only_cat:
                err(f"  카탈로그에만 있음: {only_cat}")

        # Gate 정합성 — 카탈로그는 미션별 Gate 를 준다
        cat_gates = sorted({cat["gates"][m] for m in cat["missions"]})
        if len(cat_gates) == 1:
            if mp.get("gate_id") != cat_gates[0]:
                err(f"맵: {pid} {name} 의 gate_id '{mp.get('gate_id')}' 가 카탈로그 '{cat_gates[0]}' 와 다르다")
            if "gate_ids" in mp:
                err(f"맵: {pid} {name} 은 단일 Gate 인데 gate_ids 가 있다")
        else:
            got_gates = mp.get("gate_ids")
            if got_gates is None:
                err(f"맵: {pid} {name} 은 복수 Gate({'/'.join(cat_gates)}) 인데 gate_ids 가 없다")
            elif sorted(got_gates) != cat_gates:
                err(f"맵: {pid} {name} 의 gate_ids {got_gates} 가 카탈로그 {cat_gates} 와 다르다")
            got_mg = mp.get("mission_gates")
            if got_mg is None:
                err(f"맵: {pid} {name} 은 복수 Gate 인데 mission_gates 가 없다")
            elif got_mg != {m: cat["gates"][m] for m in cat["missions"]}:
                err(f"맵: {pid} {name} 의 mission_gates 가 카탈로그 미션별 Gate 와 다르다")

        label = mp.get("phase_label_ko")
        if label is not None and label != cat["label_ko"]:
            err(f"맵: {pid} {name} 의 phase_label_ko '{label}' 가 카탈로그 '{cat['label_ko']}' 와 다르다")

    for mission in all_missions:
        if seen[mission] == 0:
            err(f"맵: 미션 {mission} 이 어느 단계에도 배정되지 않았다")
        elif seen[mission] > 1:
            err(f"맵: 미션 {mission} 이 {seen[mission]}개 단계에 중복 배정되었다")

    for mp in map_phases:
        print(
            f'  {mp.get("phase_id"):<4} {mp.get("name",""):<15} '
            f'{"~".join([mp["mission_ids"][0], mp["mission_ids"][-1]]) if mp.get("mission_ids") else "(없음)":<13} '
            f'gate={"/".join(mp.get("gate_ids", [mp.get("gate_id", "?")]))}'
        )
    print()

    # ---- 4. 오버레이 컨트롤 키 ----
    controls = amap.get("international_overlay_phase_controls", {})
    valid_ids = {mp.get("phase_id") for mp in map_phases}
    for key in controls:
        if key not in valid_ids:
            err(f"맵: international_overlay_phase_controls 의 '{key}' 가 존재하지 않는 phase_id 다")

    # ---- 5. Agent 참조 (경고) ----
    if REGISTRY.exists():
        reg = load_json(REGISTRY)
        agents = reg.get("agents", reg)
        known = {a["agent_id"] for a in agents} if isinstance(agents, list) else set()
        if known:
            for mp in map_phases:
                refs = [mp.get("lead_agent_id")] + list(mp.get("required_agent_ids", [])) + list(
                    mp.get("advisory_agent_ids", [])
                )
                for ref in refs:
                    if ref and ref not in known:
                        warn(f"맵: {mp.get('phase_id')} {mp.get('name')} 이 미등록 Agent '{ref}' 를 참조한다")

    # ---- 결과 ----
    print("=" * 52)
    if warnings:
        print(f"경고 {len(warnings)}건")
        for w in warnings:
            print(f"  WARN  {w}")
        print()
    if errors:
        print(f"불일치 {len(errors)}건")
        for e in errors:
            print(f"  FAIL  {e}")
        print()
        print("결과: 실패 — 단계 분류가 일치하지 않는다 (F-01)")
        return 1

    print(f"단계 {len(phases)} · 미션 {len(all_missions)} · 불일치 0 · 경고 {len(warnings)}")
    print("결과: 통과 — 카탈로그·스키마·workflow 맵이 일치한다")
    return 0


if __name__ == "__main__":
    # Windows 콘솔(cp949)에서도 한글·기호가 깨지지 않게 한다.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sys.exit(main())
