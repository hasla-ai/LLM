"""Forge H2 — 정본 카탈로그의 입출력 어휘 감사 (F-06 / F-07).

`mission-catalog.md` 의 입력·출력 칸은 미션 선행관계 DAG 의 유일한 근거다. 두 칸이
같은 엔티티 어휘를 쓰지 않으면 DAG 를 도출할 수 없고, 잘못 도출하면 미션이 엉뚱한
Agent 로 라우팅된다.

네 가지를 센다.

1. 전방참조   뒤 미션이 산출하는 것을 앞 미션이 입력으로 받는다 (순환의 원인, F-06)
2. 고아 산출  어느 미션도 입력으로 쓰지 않는 산출물
3. 미산출 입력 어느 미션도 산출하지 않는 입력
4. 명명 드리프트 앞선 산출물과 사실상 같은 것을 다른 이름으로 받는 입력

게이트·종단 미션의 산출은 정상적으로 고아일 수 있다. 판정하지 않고 구분만 한다.

    python tools/audit_catalog_io.py            # 보고만 (종료코드 0)
    python tools/audit_catalog_io.py --strict   # 전방참조가 있으면 1
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "03-governance" / "mission-catalog.md"

PHASE_RE = re.compile(r"^### Phase (\d+) — (.+)$")
MISSION_RE = re.compile(r"^M-\d{3}$")

# 게이트·종단 성격이라 하류 소비가 없어도 정상인 미션
TERMINAL = {"M-020", "M-030", "M-040", "M-050", "M-060", "M-070", "M-080"}


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
                "inputs": split_tokens(cells[2]),
                "outputs": split_tokens(cells[3]),
                "phase": phase,
            })
    return rows


def main() -> int:
    rows = parse_catalog(CATALOG)
    order = {r["id"]: i for i, r in enumerate(rows)}
    produced: dict[str, str] = {}
    for r in rows:
        for o in r["outputs"]:
            produced[o] = r["id"]

    def links(token: str, entity: str) -> bool:
        return token == entity or token in entity or entity in token

    forward: list[tuple[str, str, str]] = []
    unproduced: list[tuple[str, str]] = []
    drift: list[tuple[str, str, str, str]] = []

    for r in rows:
        for token in r["inputs"]:
            exact = produced.get(token)
            if exact and exact != r["id"]:
                if order[exact] > order[r["id"]]:
                    forward.append((r["id"], token, exact))
                continue
            earlier = [e for e, mid in produced.items() if order[mid] < order[r["id"]]]
            if any(links(token, e) for e in earlier):
                continue
            near = difflib.get_close_matches(token, earlier, n=1, cutoff=0.72)
            if near:
                drift.append((r["id"], token, near[0], produced[near[0]]))
            else:
                unproduced.append((r["id"], token))

    all_inputs = {t for r in rows for t in r["inputs"]}
    orphan = [
        (r["id"], r["code"], o)
        for r in rows
        for o in r["outputs"]
        if not any(links(t, o) for t in all_inputs)
    ]

    n_in = sum(len(r["inputs"]) for r in rows)
    n_out = sum(len(r["outputs"]) for r in rows)

    print("Forge H2 — 정본 카탈로그 입출력 어휘 감사")
    print("=" * 52)
    print(f"{CATALOG.relative_to(ROOT).as_posix()}  미션 {len(rows)} · 입력 {n_in} · 산출 {n_out}")
    print()

    print(f"[1] 전방참조 {len(forward)}건 — 뒤 미션이 산출하는 것을 앞 미션이 받는다")
    for mid, token, src in forward:
        print(f"      {mid} 의 입력 '{token}' 을 {src} 이 산출한다 (뒤 미션)")
    if not forward:
        print("      없음")
    print()

    core = [o for o in orphan if o[0] not in TERMINAL and int(o[0].split("-")[1]) < 91]
    print(f"[2] 고아 산출 {len(orphan)}건 — 어느 미션도 입력으로 쓰지 않는다")
    print(f"      게이트·종단 제외 {len(core)}건")
    for mid, code, o in core[:12]:
        print(f"      {mid} {code} -> {o}")
    if len(core) > 12:
        print(f"      ... 외 {len(core) - 12}건")
    print()

    print(f"[3] 미산출 입력 {len(unproduced)}건 — 어느 미션도 산출하지 않는다")
    print("      대부분 외부 데이터(현장·벤더·시장·기상)로 보이나 입력 계약이 없으면 확인할 수 없다")
    print()

    print(f"[4] 명명 드리프트 {len(drift)}건 — 앞선 산출물과 사실상 같은데 이름이 다르다")
    for mid, token, entity, src in drift:
        print(f"      {mid} 의 입력 '{token}'  ≈  {src} 의 산출 '{entity}'")
    if not drift:
        print("      없음")
    print()

    print("=" * 52)
    linked = n_in - len(unproduced) - len(drift) - len(forward)
    print(f"입력 {n_in}건 중 앞선 산출물과 연결되는 것 {linked}건 "
          f"({linked * 100 // n_in}%)")
    if forward and "--strict" in sys.argv:
        print("결과: 실패 — 전방참조가 있다 (--strict)")
        return 1
    print("결과: 보고 완료. 판정은 자격자가 한다.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sys.exit(main())
