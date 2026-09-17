# Forge H2 지식 저장·검색 파이프라인

## 1. 목적

전문가 Agent와 자문 Agent가 매번 기억에 의존하거나 일반 웹 검색을 반복하지 않고, 검증된 지식을 데이터베이스에서 불러와 근거와 함께 일하도록 한다.

```text
원문·프로젝트 자료
  → Knowledge Entry 정규화
  → 출처·판본·관할·전문영역 태깅
  → 사람 또는 권한 있는 Agent 검증
  → canonical JSON 저장
  → SQLite 파생 검색 인덱스 생성
  → Agent·단계·관할 조건으로 검색
  → 근거·판본·검증상태를 답변에 연결
  → 결정·회의·미션 결과에 기록
```

## 2. 파일

- `registry.json`: 저장소와 검색 정책
- `catalog.json`: 모든 지식의 canonical JSON 원장
- `professional-foundations.json`: 기술사 후보 20개 분야·전공서적 8종·Agent 매핑
- `formula-library.json`: 15개 기초공식의 LaTeX·ASCII·Python expression·SymPy 표현
- `offline-source-register.json`: 로컬 출처 보관·판본·해시·baseline 준비상태
- `offline-requirements.json`: GIS·계통·수소공급·기상·CAD/BIM·EPC·운영·로컬 실행환경 누락 목록
- `offline-bundle/`: 네트워크 없이 이동·검증할 수 있는 JSON 번들
- `entries.jsonl`: 초기 입력 호환용 legacy import 파일
- `pipeline.py`: 표준 라이브러리 기반 등록·검색 실행기
- `knowledge.sqlite3`: JSON 원장에서 생성되는 파생 검색 인덱스
- `agent-databases/`: Agent별로 materialize된 전문지식 JSON 데이터베이스와 manifest
- `access-policy.json`: 중앙 원장과 Agent별 DB의 읽기·쓰기 정책
- `schemas/knowledge-entry.schema.json`: 지식 항목 계약
- `schemas/knowledge-catalog.schema.json`: 중앙 JSON 원장 계약
- `schemas/agent-knowledge-database.schema.json`: Agent별 JSON 전문지식 DB 계약
- `schemas/retrieval-request.schema.json`: 검색 요청 계약
- `schemas/retrieval-result.schema.json`: 검색 결과 계약
- `schemas/professional-profile.schema.json`: 실제 사람 전문가의 자격·경험·독립성 계약

## 3. 실행

```powershell
python -m knowledge.pipeline export-json
python -m knowledge.pipeline init
python -m knowledge.pipeline ingest knowledge/catalog.json
python -m knowledge.pipeline build-agent-databases
python -m knowledge.pipeline search "수소 공정안전 HAZOP 기능안전" --agent-id AG-TEC-014 --phase safety_permit --jurisdiction international
python -m knowledge.pipeline search-formulas "power system" --top-k 5
python -m knowledge.pipeline offline-check
python -m knowledge.pipeline build-offline-bundle
```

`export-json`는 legacy JSONL을 최초 이전할 때만 사용한다. 이후 새 지식은 `catalog.json`에 새 revision으로 등록하고, 수식은 `formula-library.json`에 추가한 뒤 전문인 검증과 단위검사를 거친다.

현재 검색기는 재현 가능한 키워드·관할·단계·Agent 범위·권위등급 검색을 제공한다. 향후 임베딩 검색을 추가하더라도 최종 결과에는 동일한 `knowledge_id`, 출처 URL 또는 내부 locator, `evidence_ids`, revision, verification 상태를 반환해야 한다.

오프라인 조회는 `--offline`을 붙인다. 원문이 로컬에 없고 URL 메타데이터만 있는 자료는 검색할 수 있지만 `metadata_only`로 표시되며 기준선 승격이 차단된다. ISO·IEC·NFPA·KGS·계약·금융기관 자료는 라이선스와 관할에 맞는 원문을 `offline-source-register.json`에 등록한 뒤 다시 번들을 생성해야 한다.

## Agent별 전문지식 데이터베이스

각 Agent DB는 중앙 Source Catalog에서 자동 생성된 읽기 전용 JSON materialized view다.

```text
Agent 호출
→ 자기 Agent DB 검색
→ 필요한 경우 source_agent_ids로 타 Agent DB 조회
→ 중앙 Source Catalog에서 누락분 확인
→ 모든 결과를 동일한 source metadata와 함께 반환
```

Agent DB에 직접 지식을 쓰지 않는다. 새 지식·수정·폐기는 `catalog.json`에 새 revision으로 등록한 뒤 전체 Agent JSON DB를 재생성한다. SQLite는 검색속도를 위한 파생 인덱스일 뿐이며 지식의 원본이 아니다. 이 방식으로 전문분야별 분리와 전사적 접근성을 동시에 유지한다.

## 사서 Agent의 수식 참조

사서 Agent는 `catalog.json`에서 관련 Knowledge Entry를 찾고, `extensions.json_path`를 따라 전문 카탈로그나 수식 라이브러리를 읽는다. 수식은 임의 코드를 실행하지 않고 다음 순서로 사용한다.

```text
formula_id 조회
→ 변수·단위 확인
→ assumptions 확인
→ Python expression을 안전한 허용식으로 해석
→ 단위검사·validation_cases 실행
→ 전문인 검토 전에는 설계 기준선으로 승격하지 않음
```

## 4. 지식 사용 원칙

1. 원문을 복사해 저장하지 않고 요약·주장·출처·locator를 저장한다.
2. 법령·표준은 판본과 확인일을 저장한다.
3. 수원국 법규와 국제표준을 같은 권위로 섞지 않는다.
4. 활성 자료와 폐기·대체 자료를 구분한다.
5. 검색 결과가 없으면 추측하지 않고 `blocked` 또는 `request_more_data`로 반환한다.
6. 서로 다른 판본·출처가 충돌하면 회의를 열고 두 주장을 모두 기록한다.
7. Agent의 답변은 지식 검색 결과를 인용해야 한다.

## 5. Professional의 정의

이 시스템에서 Professional은 “정답을 많이 아는 사람”이 아니다.

```text
Professional
= 검증된 자격
  + 관련 실무경험
  + 명확한 업무범위와 권한
  + 근거를 이용한 판단
  + 이해상충 공개와 독립성
  + 결과에 대한 책임·서명
  + 최신성 재검증
```

AI Agent는 전문지식을 검색·비교·초안화할 수 있지만 Professional이 아니다. 실제 Professional Profile이 `verified`이고, 해당 범위의 인간 검토가 끝나야 기술·법무·허가·시공·운영 결과를 기준선으로 승격한다.
