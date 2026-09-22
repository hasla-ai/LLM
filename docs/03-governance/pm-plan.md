# Forge H2 프로젝트 관리계획서

문서 상태: 초안 v0.1  
기준: 대한민국, 고정식 수소발전소, 수소 공급·저장·발전·계통연계·시공·운영 전 과정  
제품 목표: 사용자가 핵심 사업조건을 입력하면 AI가 실행 가능한 미션 그래프를 만들고, 각 단계의 계산·근거·문서·승인을 추적한다.

## 1. 프로젝트 헌장

### 1.1 목적

Forge H2는 수소발전소 프로젝트를 100개의 검증 가능한 미션으로 분해하고, 다음을 자동화하는 엔지니어링 프로젝트 운영체계다.

- 요구사항에서 사업성·입지·수소공급·계통·안전·인허가 요구사항 도출
- 입력·출력·근거·가정·담당자·승인자를 미션 단위로 기록
- 결정론적 계산과 규칙 검사를 코드로 실행
- AI가 검토자료·설계 초안·인허가 매트릭스·EPC 문서를 생성
- 누락·충돌·위험·지연을 조기에 차단
- 자격 있는 사람이 최종 판단하고 승인하도록 통제

### 1.2 성공 정의

프로젝트 성공은 “AI가 멋진 문서를 만든다”가 아니라 다음을 모두 만족하는 것이다.

1. 사업자가 같은 입력으로 같은 계산을 재현할 수 있다.
2. 모든 핵심 수치에 단위·가정·근거·버전이 있다.
3. 각 인허가와 설계 산출물의 책임자가 명확하다.
4. 안전·법규·계통·환경 병목을 착공 전에 식별한다.
5. 설계변경이 발생해도 영향범위와 재승인 항목을 추적한다.
6. AI가 승인권자 또는 법정 기술책임자를 대신하지 않는다.
7. FEED·EPC·시공·시운전 자료가 하나의 프로젝트 그래프에 연결된다.

### 1.3 범위

포함 범위:

- 전력수요·판매처·운전조건
- 부지·지적·토지이용·재해·환경·물류
- 수소 생산·공급·운송·저장·압축·감압
- 연료전지·수소터빈·혼합 발전블록
- 변압기·보호계전·계통연계·전력거래
- 토목·건축·기계·배관·전기·계측제어·소방·환경
- HAZID·HAZOP·LOPA·누출·화재·폭발 검토
- 법규·KGS Code·인허가 매트릭스
- FEED·RFP·EPC·조달·품질·시공·시운전·운영 인수
- AI 플랫폼·데이터·근거·감사로그·권한·평가

제외 또는 인간 승인 필수:

- AI 단독의 최종 설계 승인
- 법정 안전거리·방출량·보호설정값의 자동 확정
- 인허가 신청의 법적 책임
- 자격자 서명 없이 IFC 도면 또는 시공 지시 발행
- 현장 안전관리자의 역할 대체

## 2. 운영 원칙

### 2.1 딸깍 실행의 정의

딸깍 한 번은 모든 것을 건너뛴다는 뜻이 아니다.

```text
ProjectIntent 입력
  → 미션 그래프 생성
  → 병렬 검토 실행
  → 누락·충돌·병목 표시
  → 다음 게이트까지 문서 자동 생성
  → 사람 승인 요청
  → 승인된 결과만 다음 단계 입력으로 승격
```

필수 입력이 없으면 시스템은 임의로 확정하지 않고 `BLOCKED` 상태와 최소 보완요청을 반환한다.

### 2.2 AI와 사람의 경계

| 구분 | AI | 사람 |
|---|---|---|
| 자료정리 | 추출·정규화·중복제거 | 원자료 진위 확인 |
| 계산 | 반복 계산·민감도 분석 | 계산모델 승인 |
| 법규 | 적용 후보·근거 검색 | 최신 법규 적용 및 법적 해석 |
| 안전 | 위험 시나리오·검토목록 생성 | 위험성평가·안전성 승인 |
| 설계 | 도면·문서 초안 | 전문분야 검토·서명 |
| 조달 | 사양 비교·평가표 | 구매·계약·보증 결정 |
| 시공 | 작업계획·검사목록 | 현장 지휘·작업허가 |
| 운영 | 경고·예측·추천 | 운전·정비·비상조치 |

## 3. 조직체계

### 3.1 의사결정 구조

```text
투자위원회 / Sponsor
        │ 사업성·예산·착공·중단 결정
        ▼
프로그램 디렉터 / PMO
        │ 일정·비용·의존성·리스크·의사결정 통합
        ├── Chief Engineer / 설계권한자
        │     ├── 수소·공정·기계·배관
        │     ├── 전기·발송배전·계통
        │     ├── 계측제어·안전계장
        │     ├── 토목·건축·구조
        │     ├── 소방·방재
        │     └── 환경·용수·배출
        ├── HSE & Regulatory Authority
        ├── Commercial & Finance
        ├── EPC & Procurement
        ├── Construction & Commissioning
        ├── Operations & Maintenance
        └── AI Product, Data & Cybersecurity
```

### 3.2 필수 역할

| 역할 | 핵심 책임 | 승인권한 | 독립성 규칙 |
|---|---|---|---|
| Sponsor | 목표·예산·사업 지속 여부 | G0·G1·G4·중단 | 안전 승인에 개입하지 않음 |
| Program Director | 전체 일정·비용·의존성·보고 | 게이트 안건 상정 | 전문 계산을 직접 승인하지 않음 |
| PMO Lead | WBS·회의·리스크·문서·변경 | PM 기준선 관리 | 모든 결정과 변경을 기록 |
| Chief Engineer | 설계기준·분야 간 기술통합 | 기술 기준선 | HSE 승인과 분리 |
| Hydrogen Process Lead | 수소 사양·공급·저장·압축 | 수소 설계 검토 | 공급사 자료를 독립 검증 |
| Mechanical/Piping Lead | 장비·배관·재료·응력 | 기계·배관 산출물 | 안전 검토와 상호검증 |
| Electrical/Grid Lead | 발전기·변압기·보호·계통 | 전기·계통 산출물 | 접속기관 조건을 근거화 |
| ICSS Lead | DCS·ESD·가스검지·인터록 | 계측제어 설계 | 안전계장 변경을 추적 |
| Civil/Structural/Architect Lead | 부지·기초·건축·배치 | 토목·건축 산출물 | 현장조건 재검증 |
| Fire & Emergency Lead | 화재·폭발·소방·대피·비상 | 방재 설계 검토 | HAZOP 조치의 독립 확인 |
| Environmental Lead | 환경영향·배출·소음·수질·폐기물 | 환경자료 | 계절조사와 협의 이력 관리 |
| HSE/Regulatory Authority | HAZID·HAZOP·PSM·법규·인허가 품질 | G3 안전·허가 게이트 | 설계 작성자와 독립 |
| Commercial Lead | 수소계약·PPA·EPC·보험·보증 | 계약 추천 | 기술평가와 가격평가 분리 |
| Finance Lead | CAPEX·OPEX·자금·수익성 | 금융안 승인 | 가정·민감도 공개 |
| Procurement Lead | RFI/RFP·벤더·장기납기·검사 | 구매추천 | 성능보증을 계약에 반영 |
| EPC Manager | FEED·상세설계·시공 통합 | EPC 실행 | 설계변경을 PMO에 통보 |
| Construction Manager | 현장·공정·작업허가·안전 | 현장 작업 통제 | 무허가 작업 중지 권한 |
| Commissioning Manager | 세척·압력시험·수소투입·성능시험 | 시운전 준비·완료 | 운영팀 인수조건 합의 |
| Operations Manager | 운전·정비·교육·비상대응 | 운영 인수 | 설계 가정의 현장 적합성 확인 |
| Product Owner | AI 제품 우선순위·사용자 가치 | 제품 백로그 | 안전·법규 게이트를 우회하지 않음 |
| AI/Platform Lead | 미션 엔진·API·UI·권한·배포 | 소프트웨어 릴리스 | 결정론적 계산과 LLM 분리 |
| Data/Evidence Lead | 데이터 모델·출처·버전·품질 | 근거 원장 기준 | 출처 없는 값 차단 |
| AI Safety/Evaluation Lead | 환각·누락·편향·평가셋 | AI 사용 승인 | 고위험 출력 자동 차단 |
| Cybersecurity/IT Lead | 접근권한·비밀·로그·백업·보안 | 보안 기준 | OT와 IT를 분리 |
| QA/QC Lead | 검사계획·부적합·품질기록 | 품질도서 승인 | 시공과 독립된 확인 |
| Independent Reviewer | 설계·안전·인허가 제3자 검토 | 독립 의견 | 작성·시공·운영 조직과 분리 |

### 3.3 최소 조직과 확장 조직

초기 제품개발팀은 다음 8개 역할로 시작할 수 있지만, 실제 발전소 착공 전에는 전문분야별 책임자를 분리해야 한다.

초기 8역할:

- Sponsor/사업책임자
- Program/PMO Lead
- Chief Engineer
- HSE/Regulatory Lead
- Hydrogen/Power Engineering Lead
- EPC/Commercial Lead
- Product/AI Lead
- Data/QA Lead

실제 건설 단계에서는 기계·배관·전기·계통·ICSS·토목·건축·소방·환경·품질·시공·시운전·운영을 각각 지정한다.

## 4. 프로젝트 게이트

| 게이트 | 목적 | 필수 입력 | 통과 산출물 | 승인자 |
|---|---|---|---|---|
| G0 Charter | 프로젝트를 시작할 가치 확인 | ProjectIntent·목표·권한 | 헌장·역할·범위 | Sponsor |
| G1 Feasibility | 사업·부지·수요 검증 | 수요·부지·수소·계통 후보 | 사업성·입지·초기 위험 보고서 | Sponsor + PMO + Chief Engineer |
| G2 Energy/Connection | 수소·발전기·계통 가능성 | 공급사·성능·접속 사전협의 | 수소·발전·계통 기준선 | Chief Engineer + Commercial |
| G3 Safety/Permit | 안전·환경·허가 경로 검증 | 개념설계·법규·HAZID·EIA 경로 | Safety Case·Permit Matrix | HSE/Regulatory Authority |
| G4 FEED/NTP | 투자·EPC·착공 결정 | FEED·견적·일정·금융 | FEED 기준선·EPC·NTP | Sponsor + Investment Committee |
| G5 IFC/Procurement | 시공 가능한 설계와 조달 | IFC·구매사양·허가조건 | IFC Set·구매발주·시공계획 | Chief Engineer + EPC Manager |
| G6 Construction/Commissioning | 안전한 설치·검사·시운전 | QA/QC·시험·준공도서 | 성능시험·인수인계 | Commissioning + QA + Operations |
| G7 COD/Operations | 상업운전과 지속관리 | 계통병입·성능·운영체계 | COD Package·운영 트윈 | Sponsor + Operations |

게이트는 통과·조건부통과·보류·중단만 허용한다. 미완료 항목을 “주의”로 남긴 채 다음 단계로 자동 이동하지 않는다.

## 5. 책임 매트릭스(RACI)

약어: `R` 실행, `A` 최종책임, `C` 협의, `I` 통보

| 산출물 | Sponsor | PMO | Chief Eng. | HSE | Commercial | EPC | AI/Data | Operations |
|---|---|---|---|---|---|---|---|---|
| 프로젝트 헌장 | A | R | C | C | C | I | C | I |
| 요구사항 기준선 | A | R | C | C | C | I | R | C |
| 입지 후보평가 | I | A | R | C | C | C | R | C |
| 수소 공급 사양 | I | C | A/R | C | R | C | C | C |
| 계통연계 검토 | I | C | A/R | C | C | C | C | C |
| 설계기준서 | I | C | A/R | C | I | C | C | C |
| HAZID/HAZOP | I | C | R | A | I | C | C | C |
| 인허가 매트릭스 | I | C | C | A/R | C | C | R | I |
| FEED | I | C | A/R | C | C | R | C | C |
| EPC RFP | C | C | C | C | A/R | C | C | I |
| 착공결정 | A | R | C | C | C | C | I | I |
| IFC 도면 | I | C | A | C | I | R | C | C |
| 시공 품질도서 | I | C | C | C | I | A/R | I | C |
| 시운전·성능시험 | I | C | A | C | C | R | C | R |
| 운영 인수 | C | C | C | C | I | R | C | A/R |
| AI 릴리스 | I | C | C | A | I | I | R | C |

안전·인허가·품질은 설계자 또는 시공자가 자기 결과를 단독 승인하지 않는다.

## 6. PMO 산출물 체계

PMO는 다음 문서를 버전과 승인상태를 가진 단일 원장으로 관리한다.

### 시작·기획

- Project Charter
- Stakeholder Register
- Requirements Baseline
- Scope/WBS
- Assumption & Constraint Log
- Master Schedule
- Cost Baseline
- Communication Plan
- Decision Log
- Risk Register

### 개발·설계

- Site Candidate Register
- GIS Evidence Pack
- Hydrogen Supply Basis
- Power & Grid Basis
- Design Basis
- Interface Register
- Equipment Register
- PFD/P&ID/SLD Register
- Permit Matrix
- KGS Applicability Matrix
- HAZID/HAZOP/LOPA Register
- Environmental Baseline
- Safety Case

### EPC·시공

- FEED Package
- RFP Package
- Bid Evaluation Matrix
- Procurement Plan
- Long Lead Register
- Baseline Schedule
- Inspection & Test Plan
- Quality Dossier
- Permit Condition Tracker
- Management of Change Log
- As-built Register
- Commissioning Plan
- Performance Test Records
- COD/Handover Package

### AI·데이터

- Mission Catalog
- Evidence Register
- Data Dictionary
- Model/Prompt Version Register
- Evaluation Dataset
- AI Output Review Log
- Access Control Matrix
- Audit Log
- Incident/Override Log
- Data Retention and Deletion Policy

## 7. 회의와 보고 체계

| 주기 | 회의 | 참석 | 결정/산출물 |
|---|---|---|---|
| 매일 | 실행 스탠드업 | 각 워크스트림 실무자 | 전일 결과·오늘 작업·차단사항 |
| 주 1회 | 통합 PMO | PMO·워크스트림 리드 | 일정·리스크·의존성·이슈 |
| 주 1회 | 설계 인터페이스 | Chief Engineer·분야 책임자 | 설계 충돌·인터페이스 결정 |
| 주 1회 | HSE/Regulatory | HSE·환경·인허가·설계 | 안전·법규·허가 차단사항 |
| 격주 | AI 제품 리뷰 | Product·AI·Data·현업 | 미션 품질·사용성·평가결과 |
| 월 1회 | Steering Committee | Sponsor·PMO·핵심 책임자 | 예산·범위·게이트·중단 여부 |
| 게이트 전 | Independent Review | 독립검토자·해당 책임자 | 통과의견·보완목록 |

모든 회의는 `결정·담당자·기한·근거·미해결 이슈`를 남긴다.

## 8. 변경관리

변경은 다음 순서로만 반영한다.

```text
Change Request
  → 영향분석(안전·법규·비용·일정·설계·AI 데이터)
  → 분야책임자 의견
  → PMO 추천
  → 승인권자 결정
  → 기준선 갱신
  → 관련 미션 재실행
  → 문서·도면·계약·시험계획 동기화
```

변경등급:

- C1: 오탈자·문서 형식 변경 — PMO 승인
- C2: 계산입력·설계조건 변경 — Chief Engineer 승인
- C3: 안전·법규·위험·허가 영향 — HSE/Regulatory Authority 승인
- C4: 예산·완공일·범위·계약 영향 — Sponsor/Steering 승인
- C5: 운영 안전·보호설정·수소조건 변경 — Operations와 HSE 공동 승인

AI는 변경 영향분석을 만들 수 있지만 승인등급을 임의로 낮출 수 없다.

## 9. 품질·AI 거버넌스

### 9.1 미션 품질조건

각 미션은 완료 전에 다음을 만족해야 한다.

- 입력 스키마 검증
- 단위 검증
- 선행 미션 완료 확인
- 사용 근거와 버전 기록
- 가정과 불확실성 표시
- 계산 재현성 확인
- 담당자와 검토자 지정
- 출력물의 다음 사용처 지정
- 차단조건 평가

### 9.2 AI 출력 등급

| 등급 | 예시 | 처리 |
|---|---|---|
| A | 파일명 추출·단위 변환·목록 정리 | 자동 저장 가능 |
| B | 계산·비교·초안 문서 | 담당자 검토 필요 |
| C | 법규 적용·위험성·설계 판단 | 자격자 검토 필수 |
| D | 안전거리·보호설정·허가 적합성·시공지시 | AI 단독 출력 금지 |

### 9.3 AI 릴리스 게이트

AI 기능은 다음을 통과해야 운영에 들어간다.

1. 정상 입력 테스트
2. 누락 입력 테스트
3. 단위·경계값 테스트
4. 악성 또는 오염 문서 테스트
5. 오래된 법규 인용 테스트
6. 근거 없는 수치 생성 테스트
7. 전문가 기준답안 비교
8. 권한 없는 승인 시도 테스트
9. 감사로그 생성 테스트
10. 롤백 테스트

## 10. 주요 리스크 운영

상세 위험은 `docs/03-governance/risk-register.md`에서 관리한다. PMO는 주 1회 확률·영향·대응·소유자를 갱신한다.

고위험 리스크는 다음 조건이면 즉시 Steering Committee에 올린다.

- G3 이후 안전 또는 허가 차단
- 임계경로 14일 이상 지연
- 예산 기준선 10% 이상 변동
- H2 공급계약 또는 계통 사전협의 실패
- 중대사고·환경위반·품질 중대부적합
- AI가 출처 없는 고위험 설계값을 생성

## 11. 제품개발과 실제 발전소 프로젝트의 분리

Forge H2 소프트웨어 개발과 실제 발전소 개발은 별도의 기준선으로 관리한다.

| 구분 | 제품개발 | 발전소 프로젝트 |
|---|---|---|
| 고객 | 사업자·설계사·EPC | 최종 사업주·관할기관 |
| 산출물 | 미션엔진·계산기·문서·UI | 허가·설계·시공·시운전 |
| 승인 | Product Owner·AI Safety | 자격자·기관·사업주 |
| 테스트 | 평가셋·회귀·보안 | 현장검사·성능시험·사용전검사 |
| 실패영향 | 기능장애·잘못된 초안 | 안전·법적·금전적 손실 |
| 출시조건 | 제품 릴리스 게이트 | 프로젝트 게이트 G0–G7 |

소프트웨어가 아직 개발 중이어도 발전소 프로젝트의 안전·법정 절차를 우회하지 않는다.

## 12. 최초 실행 순서

1. Sponsor와 Product Owner를 확정한다.
2. 대한민국 적용을 기본 관할로 기록하고 실제 사업지역을 확정한다.
3. Chief Engineer와 HSE/Regulatory Authority를 독립적으로 지정한다.
4. ProjectIntent·Mission·Evidence·Gate 스키마를 승인한다.
5. `docs/03-governance/risk-register.md`와 `docs/03-governance/decision-log.md`를 개설한다.
6. 미션 1–10을 결정론적 입력·검증·상태관리로 구현한다.
7. 미션 11–20 사업성·수요·금융 게이트를 구현한다.
8. 미션 21–40 GIS·수소공급 데이터 연결을 구현한다.
9. 미션 41–60 발전·계통·개념설계 계산기를 구현한다.
10. 미션 61–70 법규·안전·환경 검토를 구현한다.
11. 미션 71–80 FEED·EPC·조달 문서를 구현한다.
12. 미션 81–90 시공·품질·시운전 추적을 구현한다.
13. 미션 91–100 운영·정비·학습 루프를 구현한다.
14. 독립검토자가 G3와 G4 산출물을 검토한다.
15. 실제 고객 프로젝트 하나를 선정해 Shadow Mode로 검증한다.

## 13. Agent 기반 프로젝트 운영

PMO는 사람 조직의 역할을 Agent 호출 계약으로 연결한다.

- 전체 Agent 목록과 권한: `agents/registry.json`
- M-001–M-100 단계별 호출·회의·게이트: `workflow/process-agent-map.json`
- Agent 운영·독립성: `docs/04-agent-system/agent-operating-model.md`
- 기술사급 전문가·재무·법무 자문단: `docs/04-agent-system/expert-agent-catalog.md`
- 결정회의: `docs/04-agent-system/meeting-protocol.md`
- 지식 DB·검색: `knowledge/registry.json`, `knowledge/pipeline.py`, `schemas/knowledge-entry.schema.json`
- 실제 전문가 검증: `schemas/professional-profile.schema.json`

각 미션의 실행 순서는 `lead_agent → required technical agents → assurance → advisory → decision meeting → human signoff → baseline promotion`이다. Agent가 결과를 반환해도 인간 승인과 근거가 없으면 다음 기준선으로 승격하지 않는다.

## 14. 완료 정의

이 프로젝트는 다음이 모두 완료되어야 “운영 가능한 제품”으로 간주한다.

- 미션 1–100의 입력·출력·선행조건·담당자 정의
- 모든 게이트의 통과조건과 보류조건 정의
- 모든 고위험 출력의 인간승인 강제
- 근거·법규·설계·계산 버전 추적
- 요구사항에서 COD까지의 변경영향 추적
- 실제 전문 검토자 3인 이상의 평가 통과
- 대표 수소발전소 프로젝트의 Shadow Mode 검증
- 보안·백업·권한·감사로그 검증
- 현장 운영·정비 데이터의 수집·보존·폐기 정책 승인

이 문서는 사업주·PMO·설계·HSE·EPC·AI팀이 함께 승인해야 기준선이 된다.

## 15. 기술개발 교차 절단 통제

SCRUM-29 「Forge H2 수소 계산 커널」은 실제 발전소 프로젝트의 계산 실행층이다. SCRUM-39 「기존 프로그램 불변 — 시스템 보안·코드 보호 루틴 설계 및 보고」는 그 실행층과 기존 프로그램을 보호하는 별도 통제층이다.

| 통제 | 담당 | 적용 위치 | 기준선 승격 조건 |
|---|---|---|---|
| 결정론적 계산 | Chief Engineer + Data Lead | G1/G2/G3/G4/G6/G7 | 입력 스냅샷·단위·차원·계산기 버전·검증사례 |
| 코드·스키마 보호 | AI/Platform + Cybersecurity | 모든 미션·릴리스 | 변경요청·회귀검증·접근·감사 기록 |
| Evidence 계보 | Data/Evidence + 전문 Agent | 모든 계산서·Gate | 출처·판본·해시·신뢰도·Human Review |
| 불변 프로그램 통제 | PMO + Independent Reviewer | SCRUM-18/G0–G7 | 게이트 순서·승인 의미·기록 보존 확인 |

이 통제들은 기존 G0–G7에 새 게이트를 추가하지 않는다. 해당 미션과 기존 Gate의 필수 입력·차단조건으로 작동한다.
