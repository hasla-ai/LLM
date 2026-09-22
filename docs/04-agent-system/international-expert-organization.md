# 국제 수소발전소 프로젝트 전문가 조직체계

## 1. 결론

국제 프로젝트는 국내 조직을 번역해서 복사하는 것이 아니라 다음 구조로 운영한다.

```text
국내/기본 프로젝트 조직
  + 국제 프로젝트 오버레이
      ├─ Sponsor·Investment·Lender
      ├─ Owner's Engineer·Technical Authority
      ├─ 국제표준·현지 법정기술자
      ├─ Safety·Certification·Independent Assurance
      ├─ Local Permit·E&S·Stakeholder
      ├─ FIDIC·EPC·Claims·Dispute
      ├─ Trade·Tax·FX·Customs·Logistics
      └─ Data·OT Cyber·다국어 문서관리
```

국제 오버레이는 `host_country`, `international_financing`, `cross_border_contract`, `foreign_epc_or_vendor` 중 하나라도 해당하면 활성화한다.

## 2. 왜 별도 집단이 필요한가

국제 프로젝트에서는 한 명의 Chief Engineer가 모든 책임을 가질 수 없다.

1. 설계 기준은 수원국 법규와 국제표준을 함께 해석해야 한다.
2. 현지 법정 설계자·검사기관·허가기관의 책임이 별도로 존재한다.
3. 대주단은 Sponsor와 EPC와 독립된 기술실사를 요구할 수 있다.
4. 국제 EPC는 준거법·언어·지체·보증·성능·불가항력·분쟁조항이 프로젝트 성패를 좌우한다.
5. 금융종결에는 환경·사회·인권·지역사회·고충처리 조건이 들어갈 수 있다.
6. 장비·수소·압력용기의 국제운송은 수출통제·제재·위험물·통관·보험을 별도로 검토해야 한다.

## 3. 국제 전문가 집단 8개

### C01. Sponsor·Investment·Lender Council

사업주, 투자위원회, 대주단, Project Finance, Lender's Technical Advisor, 보험·정치위험, ESG 전문가로 구성한다.

결정: 금융종결, 투자, 국가위험 수용, 조건부 진행, 중단.

### C02. Owner's Engineering·Technical Authority Council

Owner's Engineer, Chief Engineer, 국제표준 관리자, 현지 등록 엔지니어, 계통코드·시장 전문가로 구성한다.

결정: 설계기준, 코드 적용, 국가별 기술 인터페이스, 성능보증 기준.

### C03. Safety·Certification·Conformity Council

HSE Authority, 공정안전, 기능안전, 화재·폭발, 독립 안전평가자, 인증·검사기관으로 구성한다.

결정: HAZOP·LOPA·SIL, Safety Case, 인증·검사·수소투입·시운전 안전성.

### C04. Local Regulatory·E&S·Stakeholder Council

현지 인허가 변호사, 현지 법정기술자, 환경·사회 전문가, 인권·지역사회 전문가, 공공정책 전문가로 구성한다.

결정: 허가 경로, 환경사회관리계획, 주민협의, 고충처리, 현지 수용성.

### C05. International EPC·Contract·Claims Council

Commercial Lead, FIDIC 변호사, EPC Manager, 계약관리자, Claims·Dispute 전문가, 기술문서관리자로 구성한다.

결정: EPC 위험배분, Employer's Requirements, 보증, 지체, 변경, 분쟁 회피.

### C06. Trade·Tax·Supply Chain Council

Procurement, 수출통제·제재, 국제세무·이전가격·환율, 위험물 물류, 보험·ECA 전문가로 구성한다.

결정: 공급국·수원국 조달, 통관, 원산지, 송금, 헤지, 장비·수소 운송.

### C07. Digital·Data·OT Cyber Council

AI/Data Lead, OT Cybersecurity, 개인정보·국경간 데이터, ICSS·SCADA, 기술번역·문서관리 전문가로 구성한다.

결정: 데이터 국외이전, OT망 분리, 접근권한, 다국어 정본, 감사로그.

### C08. Independent Assurance Council

Independent Reviewer, Lender's Technical Advisor, 인증기관, 독립 안전평가자, 국제표준 관리자 중심으로 구성한다.

결정: 독립검토 의견, No Objection, 보완 요구, Hold.

## 4. 책임권한 원칙

| 영역 | 추천 | 최종 인간 승인 |
|---|---|---|
| 국제 프로젝트 기준선 | International Program Director | Sponsor/PMO |
| 설계·코드 | Owner's Engineer·Chief Engineer | 현지 법정기술자 + 발주자 기술권한자 |
| 안전·기능안전 | Independent Safety Assessor | HSE Authority·현지 책임자 |
| 인증·검사 | Certification Agent | 공인 검사·인증기관 |
| 금융 기술실사 | Lender's Technical Advisor | 대주단 |
| 계약·분쟁 | FIDIC Counsel·Claims Agent | Sponsor·계약 당사자 |
| 환경·사회·인권 | E&S Agent | Sponsor·대주단·현지 기관 |
| 통관·제재·수출통제 | Trade Compliance Agent | 법무·준법 책임자 |
| 운영·COD | Commissioning·Operations | Sponsor·Operations·현지 기관 |

## 5. 국제 프로젝트의 표준 적용 순서

```text
수원국 법률·허가·법정기술자 요건
  → 금융계약·EPC 계약·보험 조건
  → 채택된 ISO·IEC·NFPA·ASME·API 등 국제표준
  → 발주자·EPC·공급사 사내 기준
```

국제표준이 있다고 해서 현지 법률이나 허가를 대체하지 않는다. `Standards Applicability Matrix`에는 표준명·판본·적용 조항·현지 법규와의 차이·책임자·검증근거를 함께 기록한다.

## 6. Agent 실행 규칙

- 국내형 `workflow/process-agent-map.json`을 기본으로 사용한다.
- 국제 조건이 활성화되면 `agents/international-overlay.json`을 추가로 로드한다.

### 실행 강제 규칙

국제 오버레이는 참고 목록이 아니라 Gate 입력 계약이다. `workflow/process-agent-map.json`의 `international_overlay_phase_controls`를 읽어 해당 Phase의 Agent와 출력물을 필수 호출·검증 대상으로 추가한다.

- G2: 국제표준·현지 코드 적용표, 인증·적합성 계획, 국제 계통·위험물 공급망 검토
- G3: 현지 인허가·E&S·다국어 통제와 독립 안전검토
- G4: 준거법·FIDIC·대주단 기술실사·통관·세무·다국어 계약 일치성

국제 조건이 활성화됐는데 해당 Phase의 오버레이 Agent Invocation 또는 출력 Evidence가 없으면 Gate audit은 `HOLD`로 판정한다. 오버레이 Agent의 권고는 현지 면허자·발주자 기술권한자·대주단·규제기관의 인간 승인을 대신하지 않는다.
- 각 게이트는 `gate_requirements`의 Council을 반드시 호출한다.
- 대주단·인증기관·현지 법정기술자의 의견은 Sponsor·EPC Agent의 의견과 독립적으로 기록한다.
- 다국어 문서는 번역본이 아니라 용어집·버전·우선언어·서명본을 함께 관리한다.
- 국제 전문가의 자격·등록·보험·이해상충·독립성은 사람을 배정할 때 검증한다.

## 7. 공식 기준축

- 수소 기술·대규모 수소 시스템의 국제 표준화 범위는 [ISO/TC 197 안내](https://www.iso.org/files/live/sites/isoorg/files/store/en/PUB100493.pdf)를 기준으로 확인한다.
- 수전해 수소발생기의 안전은 [ISO 22734-1:2025](https://www.iso.org/standard/82766.html)의 적용 여부를 검토한다.
- 연료전지 전력시스템은 [IEC TC 105 관련 표준](https://webstore.iec.ch/en/publication/66458)을 설비와 시험범위에 따라 검토한다.
- SIS와 기능안전은 [IEC 61511](https://webstore.iec.ch/en/publication/5527), HAZOP 절차는 [IEC 61882](https://webstore.iec.ch/en/publication/24321)를 적용성 검토 대상으로 둔다.
- 수소 화재·방호 코드는 수원국 법규와 함께 [NFPA 2 Hydrogen Technologies Code](https://link.nfpa.org/all-publications/2/2026)를 비교한다.
- 국제 EPC 위험배분은 [FIDIC Silver Book](https://fidic.org/books/epcturnkey-contract-2nd-ed-2017-silver-book-reprinted-2022-amendments)의 적용 여부를 계약전략에서 검토한다.
- 금융기관의 환경·사회 리스크는 [IFC Performance Standards](https://www.ifc.org/content/dam/ifc/doc/2023/ifc-performance-standards-2012-en.pdf)와 [Equator Principles](https://equator-principles.com/about-the-equator-principles/) 적용 여부를 확인한다.

이 기준축은 자동 승인 목록이 아니다. 프로젝트 국가·계약·금융기관·허가조건별로 적용성을 판정하고 Evidence로 남긴다.
