# Forge H2 의사결정 로그

모든 범위·기술·안전·법규·계약·AI 권한 결정은 이 문서에 누적한다. 취소된 결정도 삭제하지 않고 상태를 `Superseded`로 바꾼다.

## 결정 상태

- `Proposed`: 안건 제안
- `Under Review`: 전문 검토 중
- `Approved`: 기준선에 반영
- `Rejected`: 채택하지 않음
- `Superseded`: 후속 결정으로 대체

## 초기 기준선 결정

| ID | 일자 | 결정 | 이유 | 영향 | 승인자 | 상태 |
|---|---|---|---|---|---|---|
| D-001 | 2026-09-17 | 대한민국을 기본 관할로 삼고 실제 사업지역에서 법규를 재확정한다. | 사용자·프로젝트의 현재 기준 | 법규·인허가 커넥터 설계 | Sponsor + Regulatory | Approved |
| D-002 | 2026-09-17 | Forge H2의 목표는 완전 자동 승인 시스템이 아니라 인간 승인형 엔지니어링 코파일럿이다. | 안전·법적 책임 분리 | 모든 고위험 미션에 HUMAN_REVIEW 적용 | Sponsor + HSE | Approved |
| D-003 | 2026-09-17 | 딸깍 실행은 미션 오케스트레이션이며, 누락 입력을 우회하지 않는다. | 실제 프로젝트의 불확실성 관리 | BLOCKED 상태와 보완요청 필요 | PMO + Product | Approved |
| D-004 | 2026-09-17 | 반복 계산은 결정론적 코드로 만들고 LLM은 해석·계획·문서 초안에 사용한다. | 재현성과 감사 가능성 | 계산기와 LLM 모듈 분리 | Chief Engineer + AI Lead | Approved |
| D-005 | 2026-09-17 | 모든 AI 고위험 출력은 Evidence ID와 검토자를 요구한다. | 출처 없는 법규·수치 차단 | Evidence Gate 적용 | HSE + Data | Approved |
| D-006 | 2026-09-17 | G0–G7 단계 게이트를 통과하지 않은 결과는 다음 기준선으로 승격하지 않는다. | 조기 설계 확정 방지 | Gate Engine 구현 | PMO + Chief Engineer | Approved |
| D-007 | 2026-09-17 | 기존 Forge H2 화면은 폐기하지 않고, 새 Mission/Evidence/Gate 코어의 UI 셸로 전환한다. | 기존 작업 보존·점진적 전환 | 마이그레이션 계획 필요 | Product + Platform | Approved |
| D-008 | 2026-09-17 | 실제 건설 프로젝트 착수 전 Shadow Mode로 AI 결과를 전문 검토자와 비교한다. | 초기 AI 오류의 현장 영향 차단 | 평가셋·검토 로그 필요 | AI Safety + PMO | Approved |
| D-009 | 2026-09-17 | PM 조직의 의사결정권자, 기술사급 전문분야, 재무·법무 자문을 역할형 Agent로 등록하고 미션별로 호출한다. | 회사의 워크로드를 반복 가능한 실행 계약으로 만들기 | Agent registry·process map·호출 로그 필요 | PMO + Chief Engineer | Proposed |
| D-010 | 2026-09-17 | 모든 Agent 의견은 독립적으로 수집하고, 충돌·고위험·게이트·C3 이상 변경은 결정회의를 거친다. | 다수결식 누락과 조용한 진행 방지 | Meeting·Decision 스키마와 human signoff 필요 | PMO + HSE + Independent Reviewer | Proposed |
| D-011 | 2026-09-17 | 대한민국 기술사·법무·재무 자격은 Agent에게 부여하지 않고 실제 담당자의 자격 검증 필드로 관리한다. | AI가 법정 책임자처럼 오인되는 위험 차단 | 전문가 카탈로그와 자격 확인 절차 필요 | HSE + Legal Advisory | Proposed |
| D-012 | 2026-09-17 | 국제 프로젝트는 국내 기본 조직에 International Program·Owner's Engineer·Lender's Technical Advisor·현지 법정기술자·인증·E&S·계약·무역·데이터 Council을 오버레이한다. | 국가·금융·계약·표준·현지 책임 차이 통제 | 국제 Agent overlay와 Council별 게이트 검토 필요 | Sponsor + PMO + Chief Engineer | Proposed |
| D-013 | 2026-09-17 | 국제표준은 수원국 법규·허가·계약·금융조건의 적용성을 확인한 뒤 Standards Applicability Matrix에 등록한다. | 표준을 법규처럼 오인하는 위험 방지 | 표준판·적용조항·차이·책임자·근거 기록 | Chief Engineer + HSE + Local Authority | Proposed |
| D-014 | 2026-09-17 | 모든 Agent는 전문분야·관할·프로젝트 단계에 맞는 Knowledge Entry를 검색하고 출처·판본·검증상태를 함께 반환한다. | 기억·일반검색 의존과 근거 없는 생성 차단 | Knowledge Registry·SQLite·Retrieval Result 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-015 | 2026-09-17 | Professional은 AI가 아니라 자격·경험·범위·권한·독립성·책임·최신성 검증을 갖춘 실제 사람으로 정의한다. | 법정 책임과 AI 보조역할 분리 | Professional Profile과 인간 서명 필수 | Chief Engineer + HSE + PMO | Proposed |
| D-016 | 2026-09-17 | 중앙 Source Catalog를 진실의 원장으로 두고, 각 Agent 전문지식 DB는 읽기 전용 materialized view로 생성하며 모든 Agent가 필요한 범위에서 다른 Agent DB를 읽을 수 있게 한다. | Agent별 전문성 분리와 공통 출처 보존을 동시에 달성 | 중앙 등록·개정·검증 후 Agent DB 재생성, 교차조회 audit 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-017 | 2026-09-17 | 모든 Knowledge Entry의 canonical 저장형식은 JSON으로 통일하고, SQLite는 JSON 원장에서 생성되는 삭제 가능한 파생 검색 인덱스로만 사용한다. | AI·사람·다른 Agent가 동일한 구조화 원장을 직접 읽고 검토할 수 있게 함 | JSON Schema 검증과 재생성 파이프라인 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-018 | 2026-09-17 | 기술사·전공서적 카탈로그와 공식은 JSON 구조로 저장하고, 사용자가 제공했으나 출처·판본이 확정되지 않은 항목은 `user_provided`·`unverified`로 표시한다. | 사서 Agent가 참조할 수 있으면서 공식 기준으로 오인되지 않게 함 | 전문인 검증·단위검사·판본확인 전에는 기준선 승격 금지 | Data Lead + Chief Engineer + AI Safety | Proposed |
| D-019 | 2026-09-17 | 인터넷 단절 시 원격 출처를 조회하지 않고, 해시가 확인된 로컬 source artifact만 기준선 근거로 허용한다. metadata-only 자료는 참고로 반환하되 baseline 승격을 차단한다. | 오프라인에서도 추적성과 안전 통제를 유지 | 라이선스 문서·현행 법규·표준·계약 원문을 source pack으로 반입해야 함 | PMO + HSE + Data Lead + Legal | Proposed |
| D-020 | 2026-09-17 | 오프라인 수소발전소 건설 준비도는 출처뿐 아니라 GIS·계통·수소공급·기상·공학모델·EPC·운영·로컬 실행환경의 자료완전성을 함께 평가한다. | 지식 DB만 있고 실제 설계 입력이 없는 상태 방지 | `offline-requirements.json`의 누락 요구사항은 해당 Gate를 차단 | PMO + Chief Engineer + Data Lead | Proposed |
| D-021 | 2026-09-22 | G0는 필수 출처 원문·ProjectIntent 실제 입력·승인 기록이 확보될 때까지 `HOLD`로 유지한다. | 현재 offline-check 결과 `baseline_ready=false`이고 승인자가 아직 서명하지 않음 | G1 착수 보류, source pack·ProjectIntent·G0 검토회의 필요 | PMO + Chief Engineer + HSE + Data | Under Review |
| D-022 | 2026-09-22 | SCRUM-29 계산 커널과 SCRUM-39 코드 보호는 기존 SCRUM-18·G0–G7의 순서·의미·Evidence 구조를 변경하지 않는 교차 절단 통제로 편입한다. | 계산 재현성과 기존 프로그램 보호를 동시에 확보해야 함 | G1/G2/G3/G4/G6/G7 계산 미션과 모든 릴리스·변경 검토에 영향 | PMO + Chief Engineer + AI/Platform + Cybersecurity | Under Review |
| D-023 | 2026-09-22 | 다른 Agent가 작성한 SCRUM-29 후보 산출물은 canonical 경로로 추가하되 `app/main.py`와 기존 SCRUM-18 실행흐름은 교체하지 않는다. | 계산 결함·공식 검증을 반영하면서 기존 프로그램 불변 원칙을 지켜야 함 | H2 공식 라이브러리·독립 계산 모듈·검증 러너·F-01/F-02 결함 해결 순서 | Chief Engineer + PMO + AI/Platform | Under Review |

## 의사결정 기록 양식

새 결정은 아래 형식으로 추가한다.

```markdown
| D-XXX | YYYY-MM-DD | 한 문장 결정 | 대안과 선택 이유 | 비용·일정·안전·법규 영향 | 승인자 | Proposed |
```

상세 안건은 아래 항목을 추가로 기록한다.

- 문제와 결정이 필요한 기한
- 검토한 대안
- 입력자료와 Evidence ID
- 각 분야의 반대 의견
- 안전·법규·계통 영향
- 결정으로 변경되는 미션과 문서
- 재검토 조건
- 승인자의 이름·역할·시각

## 미해결 안건

| ID | 안건 | 필요한 입력 | 담당 | 기한 | 상태 |
|---|---|---|---|---|---|
| A-001 | 첫 실증 프로젝트의 발전방식과 규모 확정 | 수요·수소공급·부지 후보 | Sponsor + Chief Engineer | TBD | Proposed |
| A-002 | 외부 GIS·법규·계통 데이터 공급원 선정 | API·라이선스·갱신주기 | Data Lead | TBD | Proposed |
| A-003 | 독립 안전·인허가 검토기관 선정 | 후보·계약범위·예산 | HSE Authority | TBD | Proposed |
| A-004 | Mission 1–10의 JSON Schema 승인 | 스키마 초안·예시 입력 | Product + PMO | TBD | Proposed |
| A-005 | Shadow Mode에 사용할 과거 설계 프로젝트 선정 | 비식별 문서·검토자 | AI Safety Lead | TBD | Proposed |
| A-006 | SCRUM-29 커널 9개 하위 작업의 실제 구현 브랜치·검증사례·담당자 확정 | SCRUM-30–38 구현 산출물·브랜치·테스트 | Chief Engineer + AI/Platform | TBD | Proposed |
| A-007 | SCRUM-39 보호정책의 저장소 권한·비밀관리·감사로그 운영수단 확정 | 조직 저장소·실행환경·권한 매트릭스 | Cybersecurity + PMO | TBD | Proposed |
