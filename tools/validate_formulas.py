"""Forge H2 — 공식·스키마 검증 러너.

레포에 테스트가 하나도 없다. 이 스크립트가 첫 번째다.

하는 일:
  1. knowledge/*.json 의 formula-library 들을 읽어 validation_cases 를 실제로 실행한다.
  2. execution_policy.allow_dynamic_code 가 false 이므로 제한된 네임스페이스에서만 평가한다.
  3. 레포의 JSON Schema 로 각 인스턴스 문서를 검증한다 (상대 $ref 를 로컬 레지스트리로 해결).
  4. validation_cases 가 없는 공식을 경고로 보고한다 — 검증되지 않은 공식은 설계 근거가 될 수 없다.

사용:
    python tools/validate_formulas.py
    python tools/validate_formulas.py --strict   # 경고도 실패로 취급

종료코드: 0 통과, 1 실패.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 공식 평가에 허용되는 이름. 이것 말고는 아무것도 노출하지 않는다.
SAFE_GLOBALS = {"__builtins__": {}, "math": math, "abs": abs, "min": min, "max": max}

TOL_REL = 1e-9
TOL_ABS = 1e-12


def close(a: float, b: float) -> bool:
    return abs(a - b) <= max(TOL_ABS, TOL_REL * max(abs(a), abs(b)))


def load_libraries() -> list[tuple[str, dict]]:
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "knowledge", "*.json"))):
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  FAIL  {os.path.relpath(path, ROOT)} — JSON 파싱 실패: {exc}")
            continue
        if isinstance(doc, dict) and "formulas" in doc:
            out.append((path, doc))
    return out


def check_formulas(strict: bool) -> tuple[int, int, int]:
    passed = failed = warned = 0
    for path, doc in load_libraries():
        rel = os.path.relpath(path, ROOT)
        policy = doc.get("execution_policy", {})
        if policy.get("allow_dynamic_code"):
            print(f"  FAIL  {rel} — allow_dynamic_code 가 true 입니다. 정책 위반.")
            failed += 1
        print(f"\n[{rel}]  공식 {len(doc['formulas'])}개  v{doc.get('library_version')}")
        for f in doc["formulas"]:
            fid = f["formula_id"]
            expr = f.get("python", {}).get("expression")
            cases = f.get("validation_cases") or []
            if not expr:
                print(f"  FAIL  {fid} — python.expression 없음")
                failed += 1
                continue
            if not cases:
                print(f"  WARN  {fid} — validation_case 없음 ({f['name']})")
                warned += 1
                continue
            for i, case in enumerate(cases):
                inputs = dict(case.get("inputs", {}))
                try:
                    got = eval(expr, dict(SAFE_GLOBALS), inputs)  # noqa: S307
                except Exception as exc:  # noqa: BLE001
                    print(f"  FAIL  {fid}#{i} — 평가 오류: {type(exc).__name__}: {exc}")
                    failed += 1
                    continue
                want = case.get("expected")
                if want is None:
                    print(f"  WARN  {fid}#{i} — expected 없음")
                    warned += 1
                    continue
                if close(float(got), float(want)):
                    passed += 1
                else:
                    print(f"  FAIL  {fid}#{i} — got {got!r}, expected {want!r}")
                    failed += 1
        # 검증 상태가 실제 검증을 넘어서지 않는지 확인
        for f in doc["formulas"]:
            if f.get("verification_status") in ("expert_verified", "authority_confirmed"):
                if not (f.get("source_knowledge_id") and f.get("validation_cases")):
                    print(f"  FAIL  {f['formula_id']} — {f['verification_status']} 인데 "
                          "출처 또는 검증 케이스가 없습니다")
                    failed += 1
    return passed, failed, warned


def check_schemas() -> tuple[int, int]:
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError:
        print("\n[스키마] jsonschema/referencing 미설치 — 건너뜁니다 "
              "(pip install jsonschema 로 활성화)")
        return 0, 0

    schema_dir = os.path.join(ROOT, "schemas")
    registry = Registry()
    schemas = {}
    for path in glob.glob(os.path.join(schema_dir, "*.schema.json")):
        doc = json.load(open(path, encoding="utf-8"))
        res = Resource.from_contents(doc)
        if "$id" in doc:
            registry = registry.with_resource(doc["$id"], res)
        registry = registry.with_resource(os.path.basename(path), res)
        schemas[os.path.basename(path)] = doc

    # 인스턴스 문서 → 스키마 매핑
    targets = [
        ("knowledge/formula-library.json", "formula-library.schema.json"),
        ("knowledge/formula-library-h2.json", "formula-library.schema.json"),
        ("knowledge/catalog.json", "knowledge-catalog.schema.json"),
        ("knowledge/professional-foundations.json", "professional-foundations.schema.json"),
        ("knowledge/offline-requirements.json", "offline-requirements.schema.json"),
        ("knowledge/offline-source-register.json", "offline-source-register.schema.json"),
    ]
    ok = bad = 0
    print("\n[스키마 검증]")
    for rel, schema_name in targets:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path) or schema_name not in schemas:
            continue
        doc = json.load(open(path, encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schemas[schema_name], registry=registry).iter_errors(doc),
            key=lambda e: list(e.path),
        )
        if errors:
            bad += 1
            print(f"  FAIL  {rel} ({len(errors)}건)")
            for e in errors[:5]:
                print(f"        {list(e.path)}: {e.message[:110]}")
        else:
            ok += 1
            print(f"  ok    {rel}")
    return ok, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="경고도 실패로 취급")
    args = ap.parse_args()

    print("Forge H2 — 공식·스키마 검증")
    print("=" * 52)
    passed, failed, warned = check_formulas(args.strict)
    s_ok, s_bad = check_schemas()

    print("\n" + "=" * 52)
    print(f"검증 케이스 통과 {passed} · 실패 {failed} · 경고 {warned}")
    print(f"스키마 통과 {s_ok} · 실패 {s_bad}")
    if failed or s_bad or (args.strict and warned):
        print("\n결과: 실패")
        return 1
    print("\n결과: 통과")
    if warned:
        print(f"참고: validation_case 가 없는 공식이 {warned}개입니다. "
              "검증되지 않은 공식은 설계 근거로 쓸 수 없습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


