"""Forge H2 — 서지 확인 기록 검사.

`knowledge/verified-citations.json` 은 법령·기술기준의 **서지사항**(코드번호·명칭·
판번호·개정일)을 온라인에서 확인한 기록이다. **원문 확보가 아니다.**

이 검사기가 막는 것은 하나다. 서지 확인이 Evidence 로 승격되는 것.

원문(local_artifact)과 해시(sha256) 없이 `baseline_eligible: true` 가 되면 실패한다.
CLAUDE.md 1절 1항은 조문번호·판번호를 검색·확인 없이 쓰지 말라고 하지, 확인만으로
기준선이 된다고 하지 않는다. D-019 는 해시가 확인된 로컬 artifact 만 기준선 근거로
허용한다. 둘 사이의 구멍을 여기서 닫는다.

    python tools/check_citations.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CITATIONS = ROOT / "knowledge" / "verified-citations.json"

REQUIRED = [
    "citation_id", "kind", "identifier", "title_verified", "url",
    "retrieved_at", "verification_method", "verified", "not_verified",
    "local_artifact", "sha256", "baseline_eligible",
]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def main() -> int:
    if not CITATIONS.exists():
        print(f"파일 없음: {CITATIONS.relative_to(ROOT).as_posix()}")
        return 1

    doc = json.loads(CITATIONS.read_text(encoding="utf-8"))
    items = doc.get("citations", [])
    errors: list[str] = []
    warnings: list[str] = []

    print("Forge H2 — 서지 확인 기록 검사")
    print("=" * 52)
    print(f"{CITATIONS.relative_to(ROOT).as_posix()}  항목 {len(items)}건")
    print()

    seen: set[str] = set()
    eligible = 0
    for c in items:
        cid = c.get("citation_id", "<id 없음>")
        for f in REQUIRED:
            if f not in c:
                errors.append(f"{cid}: 필수 필드 '{f}' 가 없다")

        if cid in seen:
            errors.append(f"{cid}: citation_id 중복")
        seen.add(cid)

        # 핵심 규칙 — 원문·해시 없이 기준선 자격을 주지 않는다
        if c.get("baseline_eligible"):
            eligible += 1
            if not c.get("local_artifact") or not c.get("sha256"):
                errors.append(
                    f"{cid}: 원문(local_artifact)과 해시(sha256) 없이 "
                    f"baseline_eligible=true 다. 서지 확인은 Evidence 가 아니다"
                )
        sha = c.get("sha256")
        if sha and not SHA_RE.match(str(sha)):
            errors.append(f"{cid}: sha256 형식이 아니다")
        if c.get("local_artifact"):
            p = ROOT / c["local_artifact"]
            if not p.exists():
                errors.append(f"{cid}: local_artifact 파일이 없다 — {c['local_artifact']}")

        d = c.get("retrieved_at")
        if d and not DATE_RE.match(str(d)):
            errors.append(f"{cid}: retrieved_at 이 YYYY-MM-DD 가 아니다 — {d}")

        for f in ("verified", "not_verified"):
            v = c.get(f)
            if not isinstance(v, list) or not v:
                errors.append(f"{cid}: '{f}' 가 비어 있다. 무엇을 확인했고 무엇을 못 했는지 남긴다")

        if not c.get("current_edition"):
            warnings.append(f"{cid}: 현행 판번호가 비어 있다 — 인용 시 판번호를 쓸 수 없다")
        if not c.get("effective_date"):
            warnings.append(f"{cid}: 시행일이 비어 있다")
        if c.get("statutory_basis") is None:
            warnings.append(f"{cid}: 근거 법령 미확인")

    for c in items:
        mark = "기준선가능" if c.get("baseline_eligible") else "서지확인만"
        ed = c.get("current_edition") or "판번호 미확인"
        print(f"  {c.get('citation_id',''):<18} {c.get('identifier',''):<14} {ed:<26} [{mark}]")
    print()

    if warnings:
        print(f"경고 {len(warnings)}건 — 인용에 필요한 항목이 비어 있다")
        for w in warnings[:12]:
            print(f"  WARN  {w}")
        if len(warnings) > 12:
            print(f"  ... 외 {len(warnings) - 12}건")
        print()

    print("=" * 52)
    if errors:
        for e in errors:
            print(f"  FAIL  {e}")
        print()
        print("결과: 실패")
        return 1

    print(f"항목 {len(items)} · 기준선 자격 {eligible} · 오류 0 · 경고 {len(warnings)}")
    print("결과: 통과")
    print()
    print("주의: 서지 확인은 원문 확보가 아니다. 조문 내용·적용 범위·적합성 판정은")
    print("자격자가 원문으로 한다. 기준선 근거로 쓰려면 원문을 반입하고 해시를 등록한다.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sys.exit(main())
