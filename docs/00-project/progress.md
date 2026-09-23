# Forge H2 Enterprise 진행 기록

신규 프로젝트 ID: **FHZ-ENTERPRISE-001**  
현재 상태: **INITIATED — 요구사항·미션·스키마 기준선 작성 중**  
기존 `app/`·`forge_model/`·`data/`는 `legacy_prototype`으로 보존한다.

현재 구현 단계: **33/50 — 건설 프로젝트 Agent 운영 기준선·계산 커널·보호 감사**

- 1–5: 레거시 프로토타입의 채팅, 프로젝트 탐색, 컨텍스트, 파일·Artifact·검증
- 6–8: 수소발전소 도메인, 수소량·면적 공식, 예비 설계문서
- 9–12: 설계 블록, GIS 지도, 공간 그래프 API, SQLite 누적 저장·작업 보드
- 13–15: 스냅샷 JSON, 프로젝트 ID 분리, 공간 그래프 기반 예비 설계문서
- 16: 프로젝트별 수소발전 프로필 저장
- 17: 지도 발전 블록 용량과 수치 예비검토 연결
- 18: 설비 간 WGS84 직선거리·공정 연결거리 검토
- 19: 누락 설비·근접 배치 후보 자동 검토 신호
- 20: 지도에서 통합 예비검토와 Markdown 설계문서 다운로드
- 21: PM 의사결정권자·기술사급 기술전문가·재무·법무 자문 Agent 53개 등록
- 22: M-001–M-100 단계별 주관·필수 전문가·자문·회의·게이트 호출 맵 연결
- 23: Agent 호출·결정회의·인간서명용 JSON Schema와 예시 추가
- 24: 비전문가용 Report 1과 기술전문가용 Report 2 작성
- 25: Professional Profile·Knowledge Entry·Retrieval Request/Result 스키마 추가
- 26: 11개 초기 지식 항목을 SQLite 지식 DB에 등록하고 Agent 범위·단계·관할 검색 검증
- 27: 중앙 Source Catalog를 기준으로 53개 국내 기본 Agent와 19개 국제 Overlay Agent의 전문지식 SQLite DB를 materialize하고 교차 Agent 읽기정책·manifest 검증
- 28: 모든 지식의 canonical JSON catalog와 Agent별 JSON 전문지식 DB를 생성하고 SQLite는 파생 검색 인덱스로 격하
- 29: 사용자 제공 기술사·전공서적 카탈로그와 15개 기초공식의 LaTeX·Python·SymPy JSON 라이브러리를 사서 Agent 참조경로에 연결
- 30: 오프라인 출처 레지스터·해시 번들·원격 fetch 차단·로컬 출처 부재 시 baseline 차단 정책과 `offline-check`/`build-offline-bundle` 실행기 추가
- 31: 오프라인 건설에 필요한 GIS·계통·수소공급·기상·CAD/BIM·EPC·운영·로컬 런타임 요구사항 10개를 JSON gap register로 추가
- 32: Sola 검증루틴을 반영하여 Evidence provenance·Gate audit·Human-in-the-loop·오프라인 번들 검증·국제 오버레이·병렬/재기준선·AI Ensemble 정책을 실행 기준선으로 추가
- 33: SCRUM-29 결정론적 수소 계산 커널과 Quantity 계약을 G1/G2/G3/G4/G6/G7 미션에 연결하고, SCRUM-39 기존 프로그램 불변·코드 보호 읽기 전용 감사루틴을 추가

PM 기준선 추가:

- `docs/03-governance/pm-plan.md`: 회사형 조직·역할·게이트·RACI·변경·품질관리
- `docs/03-governance/requirements-baseline.md`: 제품 요구사항·수용조건
- `docs/03-governance/mission-catalog.md`: 100개 함수형 미션·공통 실행계약
- `docs/03-governance/evidence-standard.md`: 근거 등급·검증·데이터 계보
- `docs/03-governance/gate-criteria.md`: G0–G7 진입·통과·차단조건
- `schemas/`: Agent·API·사람이 공유하는 JSON Schema 정본과 예시
- `agents/registry.json`: PM 의사결정권자·기술사급 전문가·재무·법무 자문 Agent 레지스트리
- `workflow/process-agent-map.json`: M-001–M-100 단계별 Agent 호출·회의·승인 흐름
- `docs/04-agent-system/`: Agent 운영·전문가 카탈로그·회의 프로토콜
- `agents/international-overlay.json`: 국제 PMO·Owner's Engineer·대주단·현지·E&S·FIDIC·통관·인증 오버레이
- `docs/04-agent-system/international-expert-organization.md`: 국제 프로젝트 8개 전문가 Council과 게이트별 구성

계산 커널 기준선 추가 (2026-09-22):

- `CLAUDE.md`: 저장소 작업 규칙·근거등급·미해소 결함·교차 검증 기준값
- `docs/02-engineering/h2-calc-kernel.md`: 계산 커널 설계 — 8기본차원·근거등급 전파·불확실도
- `docs/02-engineering/h2-calc-kernel-overlay.md`: SCRUM-29 controlled_overlay 기준선 (기존 문서를 이 경로로 이동)
- `docs/03-governance/findings-2026-09-22.md`: 단계 분류 충돌과 계산 결함 검토 결과
- `docs/03-governance/scrum-cross-cutting-integration.md`: SCRUM-29·SCRUM-30–38·SCRUM-39와 G0–G7 전체 연결 기준선
- `docs/03-governance/mission-library-100.json`: 선행관계·완료기준·차단조건이 채워진 미션 라이브러리 참고본
- `knowledge/formula-library-h2.json`: 수소 플랜트 고유식 18개, 검증 케이스 22개
- `tools/validate_formulas.py`: 공식 검증 케이스 실행 + 스키마 검증 (레포 최초 테스트)
- `app/calc.py`: 총발전단/순출력·잔압·저장밀도를 고친 계산 모듈
- `security/audit.py`: 보호 자산·Gate·Evidence·공식·계산기 기준값 출처를 검사하는 읽기 전용 감사
- `app/static/h2-module.html`: 계산 워크벤치
- `app/static/h2-mission-engine.html`: 100개 미션 게이팅 엔진

다음 개발 단계: **D-035 2차 회의록의 기계적 재생성 조치와 DR-01~DR-10 자격자 결정·Gate Evidence 등록 → F-02 기준선 승격 검토 → 커널 Python 이식(SCRUM-38)**

주의: 현재 결과는 예비 검토용이며 실제 설계·안전·인허가 판단은 자격자가 수행해야 합니다.

## 실행 체크포인트 — 2026-09-22

- G0 Jira 업무 `SCRUM-19`를 `검토 중`으로 유지하고 JEON을 담당자로 지정했다.
- `python -m knowledge.pipeline offline-check`를 실행했다.
- 현재 결과는 catalog 13건, source register 13건, 로컬 원문 4건, metadata-only 9건, `baseline_ready=false`다.
- G0 Gate 실행 기록을 `data/project-records/FHZ-ENTERPRISE-001/gates/G0-2026-09-22.json`에 저장했다.
- G0는 `not_ready`로 유지한다. ProjectIntent 실제 입력, 오프라인 필수 출처 원문, 승인자 검토 기록이 확보될 때까지 G1로 승격하지 않는다.
- 사용자 지시에 따라 출처 반입과 승인 검토를 우선순위로 정하고, 공식 공개 자료 7건을 `knowledge/source-cache/`에 캐시했다. 전체 라이선스 표준 원문이 아니므로 해당 항목은 계속 `metadata_only`다.
- G0 검토회의와 HOLD 권고를 `data/project-records/FHZ-ENTERPRISE-001/meetings/MTG-G0-2026-09-22.json` 및 `data/project-records/FHZ-ENTERPRISE-001/decisions/DEC-G0-HOLD-2026-09-22.json`에 기록했다.
- PMO·Chief Engineer·HSE·Product·Data·AI Safety·Independent Reviewer Agent의 오프라인 사전검토 7건을 `data/project-records/FHZ-ENTERPRISE-001/invocations/`에 기록했다. 매칭 부족·KGS 원문 부족·인간 서명 필요를 이유로 G0 HOLD를 유지한다.
- Sola 검토 6개 항목을 `data/project-records/FHZ-ENTERPRISE-001/external-reviews/SOLA-G0-2026-09-22.json`으로 기록했다. `AG-AI-001`·`AG-GOV-001` 호출을 추가하고 회의 참가자·필수 Agent·Invocation 정합성 검사를 연결했다.
- `verify-offline-bundle` 결과는 119개 파일·해시·초과/누락 파일·source register 정합성 모두 통과했다. 단, 출처 9건은 여전히 `metadata_only`이므로 `offline-check`의 `baseline_ready=false`는 유지한다.
- `audit-gate`는 7개 G0 Evidence가 모두 `unverified`이고 인간 검토가 대기 중임을 검출하여 `hold_until_audit_errors_resolved`를 반환했다. 이는 실패가 아니라 문서 존재만으로 G0가 통과되지 않는지 확인한 정상 차단이다.
- SCRUM-29 커널 기준선은 `docs/02-engineering/h2-calc-kernel-overlay.md`와 `knowledge/calculation-kernel.json`에 기록하고, SCRUM-39 보호 기준은 `security/protection-policy.json`과 `python -m security.audit`에 연결했다. 기존 SCRUM-18과 G0–G7의 순서·의미는 변경하지 않았다.
- `python tools/validate_formulas.py --strict`를 실행했다. 검증 케이스 37건 통과·0건 실패·0건 경고, 스키마 6건 통과·0건 실패다. 일반공식 15개와 H2 공식 18개 모두 validation case를 갖는다.
- `python -m unittest discover -s tests -v`는 4건 통과했고, `.github/workflows/quality.yml`이 Python 3.11·3.12에서 같은 검사를 실행한다.
- F-02 선행관계 결정지 29건은 모두 `confirmed`로 반영되어 모호 0건이 됐다. D-029에 따라 M-046이 `PreliminarySLD`를 산출하고 M-047이 이를 사용하도록 반영했으며, M-058은 `DetailedSLD`를 산출한다. 미션 정의는 전방참조 0건과 dependencies 101건으로 재생성한다.
- D-030에 따라 카탈로그만 근거로 100개 미션의 목적·완료기준·차단조건을 `mission-content-draft.json`에 작성하고 생성 정의에 병합했다. 해당 내용은 자격자 검토 전 초안이며, 입력·출력 schema_ref와 quality_checks는 다음 F-02 작업으로 남아 있다.
- D-031에 따라 100개 미션의 입력·출력 schema_ref와 quality_checks를 `mission-contract-draft.json`에 작성하고 생성 정의에 병합했다. 현재 미션 정의는 스키마 100/100·내용 완결 100/100이며, 실제 JSON Schema 등록과 owner 검토 전까지는 기준선이 아니다.
- D-032에 따라 카탈로그 토큰을 `schemas/mission-contracts.schema.json`의 200개 draft 정의로 등록하고 `schemas/registry.json`에 추가했다. `mission-owner-review-queue.json`에 100개 담당자 검토 항목을 모두 `pending`으로 생성했으며, 실제 승인 기록 전까지 기준선 승격을 차단한다.
- D-033에 따라 카탈로그에서 고유 입출력 토큰 249건을 생산·소비 미션과 함께 `entity-contract-review-queue.json`에 등록했다. 타입·단위·널 허용·근거 요건은 추측하지 않고 모두 `pending_owner_review`로 남겼으며, 이 큐와 owner 검토 결과가 채워지기 전에는 F-02를 기준선으로 승격하지 않는다.
- D-034에 따라 100개 미션과 249개 토큰 각각의 제안 판정·근거·Gate Evidence 제안·검토 질문·한계를 `qualified-review-report-missions.*` 및 `qualified-review-report-entities.*`에 기록했다. 모든 결정은 `proposed_not_approved`이며 자격자 서명 전 기준선 승격은 차단한다.
- D-035 2차 회의록에서 IR-01·IR-02·IR-03의 재현 결과와 기계적 후속조치를 분리 기록했다. 정확일치는 실행계약 기준, 부분일치는 명명 드리프트 감사로 유지하며, DR-01·DR-02·DR-03 등 안전·계통·시운전 계약 공백은 자격자 결정 전 `HOLD`로 남긴다.
