# Report 2 — Forge H2 Enterprise 기술·운영 아키텍처 보고서

## 1. 문서 목적

본 보고서는 Forge H2 Enterprise를 단순한 소프트웨어 제품이 아니라, 수소발전소의 개발·설계·조달·시공·시운전·상업운전·정비를 수행하는 **프로그램화된 EPC·Owner’s Engineering 운영체계**로 정의한다.

핵심 목표는 다음의 폐쇄루프를 구축하는 것이다.

```text
ProjectIntent
→ Mission Graph
→ Agent Plan
→ Knowledge Retrieval
→ Domain Deliberation
→ Decision Meeting
→ Human Signoff
→ Stage Gate
→ Baselined Output
→ Next Mission Input
```

## 2. 운영 대상

### 2.1 프로젝트 생애주기

| Layer | 주요 업무 | 대표 Gate |
|---|---|---|
| Intake | 전력수요·부지·수소·운전조건 정규화 | G0 |
| Business | CAPEX/OPEX·수익성·PPA·Project Finance | G1 |
| Site | GIS·지적·토지권리·환경·물류·재해 | G1/G2 |
| Hydrogen | 생산·공급·압축·저장·감압·순도·물질수지 | G2/G3 |
| Power/Grid | 발전블록·변압·보호계전·계통연계·전력시장 | G2/G4 |
| Safety/Permit | HAZID·HAZOP·LOPA·SIL·PSM·EIA·허가 | G3 |
| FEED/EPC | Design Basis·FEED·RFP·견적·계약·NTP | G4/G5 |
| Construction | IFC·조달·QA/QC·ITP·시공·MOC | G5/G6 |
| Commissioning | Pre-commissioning·수소투입·성능시험·인수 | G6 |
| Operations | COD·운전·정비·비상·성능·디지털 트윈 | G7 |

### 2.2 조직 계층

```text
Sponsor / Investment Committee
└─ Program Director / PMO
   ├─ Chief Engineer / Design Authority
   │  ├─ Hydrogen & Process
   │  ├─ Mechanical & Piping
   │  ├─ Electrical & Grid
   │  ├─ ICSS / SIS / OT Cyber
   │  ├─ Civil / Geotechnical / Structural
   │  ├─ Fire / Process Safety / Construction Safety
   │  └─ Environment / Water / Logistics
   ├─ HSE & Regulatory Authority
   ├─ Commercial / Finance / Procurement / Legal
   ├─ EPC / Construction / Commissioning / Operations
   ├─ QA/QC / Independent Review / Certification
   └─ AI Platform / Data-Evidence / AI Safety
```

국제 프로젝트에서는 위 조직에 다음 오버레이를 추가한다.

```text
International Program Director
├─ Owner's Engineer / Technical Authority
├─ Lender's Technical Advisor / Independent Engineer
├─ Local Licensed Engineer / Local Regulatory Counsel
├─ International Standards & Code Manager
├─ Certification / Conformity Assessment
├─ E&S / Human Rights / Community
├─ FIDIC / Claims / Dispute
├─ Export Control / Sanctions / Customs
├─ Cross-border Tax / FX / ECA / Political Risk
└─ Data Privacy / OT Cyber / Technical Translation
```

## 3. Agent 실행 모델

### 3.1 Agent Definition

`Agent Definition`은 사람 또는 AI가 어떤 역할을 수행하는지를 선언한다.

필수 구성요소:

- `agent_id`: 변경되지 않는 식별자
- `category`: governance, technical, advisory, assurance, platform
- `mode`: decision owner proxy, expert advisor, reviewer 등
- `domains`: 전문 분야
- `qualification_expectation`: 실제 사람에게 요구되는 자격 수준
- `authority`: 준비·추천·승인 요청 범위
- `consultation_rules`: 필수 협의자와 escalation 대상
- `prohibited_actions`: AI가 하면 안 되는 행동
- `review_policy`: 독립검토·인간검토 조건

현재 기본 Agent 53개와 국제 오버레이 Agent 19개를 등록했다.

### 3.2 Agent Invocation

Agent 호출은 단순 API 요청이 아니라 감사 가능한 실행기록이다.

```json
{
  "invocation_id": "CALL-M-041-AG-TEC-001-0001",
  "agent_id": "AG-TEC-001",
  "mission_id": "M-041",
  "context_refs": ["EVD-H2-SUPPLY-001"],
  "position": {"recommendation": "proceed_with_conditions"},
  "blockers": [],
  "human_review": {"required": true, "status": "pending"}
}
```

### 3.3 Meeting Deliberation

다음 상황에서는 Agent를 병렬 호출한 뒤 회의를 생성한다.

- risk class C/D
- cross-domain conflict
- stage-gate review
- C3 이상 Management of Change
- safety·permit·contract·construction·operations control decision

회의는 다수결 엔진이 아니다. 각 Agent의 `position`, `evidence_refs`, `assumptions`, `dissent`, `conditions`를 보존하고, 인간 결정권자가 선택한다.

## 4. 지식 데이터베이스 아키텍처

### 4.1 Knowledge Layer

| 계층 | 내용 | 대표 권위 |
|---|---|---|
| Normative | 법령·허가·공식 표준 | T0/T1 |
| Technical | Design Basis·계산·시험·벤더 | T2 |
| Commercial | 계약·금융·보험·조달 | T3 |
| Operational | SOP·정비·사고·교훈 | T2/T4 |
| Project | 승인된 기준선·결정·미션 | 프로젝트 승인상태 |

각 Knowledge Entry는 `knowledge_id + revision`을 기본 키로 사용한다. 이전 판본을 덮어쓰지 않고 `superseded`로 전환한다.

### 4.2 Knowledge Entry

```text
KnowledgeEntry
├─ identity: knowledge_id, schema_version, revision
├─ scope: domains, jurisdictions, languages
├─ authority: authority_level, source_kind, publisher
├─ provenance: URL, locator, captured_at
├─ applicability: agent_ids, roles, phases, gates
├─ content: summary, claims, keywords
├─ verification: status, reviewer, evidence_ids
└─ access: classification, allowed_agent_categories
```

### 4.3 중앙 원장과 Agent별 전문지식 DB

`knowledge/catalog.json`은 모든 Knowledge Entry와 원출처 메타데이터를 보존하는 중앙 Source Catalog다. 등록된 53개 국내 기본 Agent와 19개 국제 Overlay Agent에는 각각 `knowledge/agent-databases/{agent_id}.json`이 materialized view로 생성된다. `knowledge.sqlite3`는 이 JSON 원장에서 재생성되는 검색용 파생 인덱스다.

```text
중앙 Source Catalog JSON (write / revision / verification)
        │
        ├─ AG-TEC-014.sqlite3  공정안전·HAZOP 전문 범위
        ├─ AG-HSE-001.sqlite3  HSE·인허가 전문 범위
        ├─ AG-FIN-001.sqlite3  Project Finance 전문 범위
        └─ ... 총 72개 Agent JSON DB (read)
```

각 Agent는 자기 DB를 우선 조회하고, `source_agent_ids`로 다른 Agent DB를 교차조회할 수 있다. 중앙 원장에서 항목이 `superseded` 또는 `withdrawn`이 되면 Agent DB를 재생성하여 오래된 active 항목이 남지 않도록 한다. 따라서 Agent DB는 독립적인 진실이 아니라 출처를 보존한 전문분야별 읽기 모델이다.

### 4.4 Retrieval Pipeline

```text
1. Ingest
   원문·계약·시험자료·프로젝트 문서 등록
2. Normalize
   제목·판본·관할·언어·전문분야 정규화
3. Chunk/Claim
   문서를 Agent가 사용할 수 있는 주장 단위로 분리
4. Verify
   출처·판본·적용범위·전문가 검토상태 확인
5. Store
   canonical JSON 원장 저장
6. Index
   Agent별 JSON DB와 SQLite 파생 검색색인 생성
7. Retrieve
   Agent 호출 시 동일한 필터로 후보 지식 검색
8. Rank
   질의 일치도·권위등급·관할·단계·Agent 적용범위·검증상태로 재정렬
9. Cite
   검색 결과에 knowledge_id·URL 또는 내부 locator·Evidence ID·revision·verification을 붙임
10. Review
   상충 자료·낮은 권위·만료 자료는 회의 또는 BLOCKED로 전환
11. Learn
   승인된 결정·운영교훈을 새 revision으로 등록
```

현재 지식 원장은 JSON이며, SQLite는 결정론적 lexical retrieval을 위한 파생 인덱스다. 향후 embedding/vector retrieval을 추가할 수 있지만, 검색 결과의 출처·판본·검증·적용범위 계약은 변경하지 않는다.

### 4.5 Offline Execution Contract

오프라인 실행은 단순한 네트워크 오류 처리가 아니다. `offline-source-register.json`이 각 Knowledge Entry의 로컬 원문 보유상태·판본·SHA-256을 관리하고, `offline-check`가 기준선 준비상태를 판정한다.

```text
offline=true
→ remote fetch 금지
→ 자기 JSON DB·교차 Agent JSON DB·중앙 catalog만 조회
→ local_artifact와 hash 확인
→ metadata_only / missing_local이면 검색은 허용하되 baseline 승격 차단
→ 모든 파일을 offline-bundle/manifest.json으로 무결성 확인
```

현재 번들은 13개 Knowledge Entry와 72개 Agent JSON DB를 포함하지만, ISO·IEC·NFPA·KGS·FIDIC·IFC·Equator 원문은 라이선스·관할별 반입 전이므로 `baseline_ready=false`다. 실제 건설 기준선으로 사용하려면 해당 원문과 프로젝트별 허가·계약·계통 문서를 로컬 source pack으로 등록해야 한다.

## 5. 검색 정책

검색 요청은 다음 context를 반드시 포함한다.

```text
request_id
project_id
requesting_agent_id
phase
jurisdiction
query
knowledge_type/domain filters
purpose
```

검색 결과는 다음을 반드시 반환한다.

```text
knowledge_id
rank / score
summary
source.publisher
source.source_kind
source.url 또는 source.locator
source.evidence_ids
revision
verification_status
relevance_reasons
```

검색 우선순위는 다음과 같다.

```text
T0 법령·허가
> T1 공식표준·공공기관
> T2 인증시험·전문가 자료
> T3 공급사·계약
> T4 내부 교훈·AI 초안
```

단, 권위가 높아도 현재 관할·설비·판본에 적용되지 않으면 사용하지 않는다.

## 6. Professional의 기술적 정의

Professional Profile은 실제 인간의 책임성과 역량을 데이터 계약으로 표현한다.

```text
Professional
= Qualification Validity
∧ Relevant Experience
∧ Scope Competence
∧ Authority Boundary
∧ Evidence-Based Judgment
∧ Independence / COI Control
∧ Accountability / Signoff
∧ Currency Review
```

필드:

- 자격명·발급기관·유효기간·검증 Evidence
- 관할·등록·설계/감리/검사 권한
- 관련 실무연수와 전문범위
- 이해상충 신고와 독립검토 가능 여부
- 검증자·검증일·다음 재검토일

따라서 LLM의 출력 정확도만으로 Professional을 선언할 수 없다. LLM은 `expert_advisor` 또는 `workflow_controller`일 수 있으나, `human_approved`를 생성하는 주체는 실제 책임자다.

## 7. 국제 기준의 적용성

- ISO/TC 197: 수소 생산·저장·운송·측정·사용의 국제표준화 범위
- ISO 22734-1: 수전해 수소발생기 안전
- IEC TC 105: 연료전지 기술 및 전력시스템 시험·안전
- IEC 61511: 공정산업 SIS·기능안전 생명주기
- IEC 61882: HAZOP 준비·검토·문서화·후속조치
- NFPA 2: 수소 기술·화재·방호 적용성
- FIDIC Silver Book: EPC/Turnkey 위험배분·Employer’s Requirements·Particular Conditions
- IFC Performance Standards: 환경·사회 성과관리
- Equator Principles: 프로젝트금융 E&S 실사·독립검토·모니터링

이 표준들은 자동 적용 목록이 아니다. 수원국 법규·허가·계약·금융기관 조건과의 관계를 `Standards Applicability Matrix`로 판정한다.

## 8. 운영 통제

1. Knowledge Entry가 `active`가 아니면 기본 검색에서 제외한다.
2. 검증되지 않은 지식은 기술·안전·허가 기준선에 사용할 수 없다.
3. 동일 주제의 판본 충돌은 자동으로 숨기지 않는다.
4. 관할이 맞지 않는 표준은 참고자료로만 표시한다.
5. AI가 근거에 없는 수치를 생성하면 `blocked`와 AI Safety 이벤트를 생성한다.
6. Professional이 승인한 결정은 Decision Log·Gate·Mission Run과 연결한다.
7. Knowledge DB 자체도 변경관리 대상이며, 등록·수정·폐기 모두 감사로그를 남긴다.

## 9. 운영 KPI

- Evidence citation coverage
- Retrieval precision@k
- Outdated-source detection rate
- Jurisdiction mismatch rate
- Unresolved dissent count
- Human review turnaround time
- Blocked-before-baseline rate
- Knowledge revision latency
- Professional verification completion
- Decision-to-source traceability
