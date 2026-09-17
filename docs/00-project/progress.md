# Forge H2 Enterprise 진행 기록

신규 프로젝트 ID: **FHZ-ENTERPRISE-001**  
현재 상태: **INITIATED — 요구사항·미션·스키마 기준선 작성 중**  
기존 `app/`·`forge_model/`·`data/`는 `legacy_prototype`으로 보존한다.

현재 구현 단계: **31/50 — 건설 프로젝트 Agent 운영 기준선**

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

다음 개발 단계: **Knowledge Retrieval 결과를 Agent Invocation·Meeting·Decision 실행기에 연결하고 인간 검토 큐 구현**

주의: 현재 결과는 예비 검토용이며 실제 설계·안전·인허가 판단은 자격자가 수행해야 합니다.
