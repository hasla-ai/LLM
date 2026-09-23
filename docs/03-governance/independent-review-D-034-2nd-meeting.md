# D-034 독립검토 2차 회의록

문서 ID: FHZ-MTG-D034-002  
회의일: 2026-09-23  
대상: D-034 자격자 검토 보고서 및 `independent-review-D-034.md`  
상태: `proposed_not_approved` — 자격자 승인·서명 전 회의록  
결정 참조: D-035 · 보충 접수 D-036

---

## 1. 회의 목적과 범위

1차 독립검토에서 발견한 IR-01~IR-07 및 DR-01~DR-10을 재현하고, 다음을 구분한다.

- 기계적으로 수정·재생성할 수 있는 보고서 품질 문제
- 정본 어휘·계약의 정책을 정해야 하는 거버넌스 문제
- 공정안전·계통·시운전 자격자가 판단해야 하는 보류 안건

이 회의록은 자격자 승인을 대신하지 않는다. `owner_decision`, `decision_ref`, Gate Evidence
서명은 기록하지 않으며, 실행 가능한 후속조치와 사람의 결정이 필요한 안건만 등록한다.

검토 역할 범위: PMO, Chief Engineer, HSE/Process, Electrical/Grid, Commissioning, Data/AI,
Mission owners, Independent Reviewer. 실명 참석·서명은 별도 회의 기록이 없으므로 이 문서에
추정해 적지 않는다.

---

## 2. 전수 재검증 결과

다음은 저장소의 현재 파일을 다시 읽어 재현한 결과다.

| 항목 | 재검증 결과 |
|---|---:|
| 미션 보고서 JSON entries | 100 |
| 미션 보고서 Markdown `## M-` 섹션 | 100 |
| 토큰 보고서 JSON entries | 249 |
| 토큰 보고서 Markdown 표 행 | 249 |
| 미션별 목적·완료기준·차단조건·품질검사 누락 | 0 |
| 토큰별 제안·한계·확인 질문 누락 | 0 |
| 미션·토큰 `owner_decision` 기록 | 0 |
| 미션·토큰 `decision_ref` 기록 | 0 |
| 미션 정본 대조(`code/gate/owner/inputs/outputs`) | 불일치 0 |
| 미션 dependencies 파생본 대조 | 불일치 0 |
| 토큰 고유값 | 249 |
| 산출 토큰 | 102 |
| 외부 입력 토큰(정확일치 기준) | 147 |
| 토큰 타입 신뢰도 | low 228 · medium 21 · high 0 |
| 단위 후보 | 33/249 |

### 2.1 IR-03 수치의 해석

IR-03은 수치 오류가 아니라 판정 기준의 혼용으로 확인한다.

- `qualified-review-report-entities.json`의 `output_only 92`와 `external_input 147`은
  **정확히 같은 토큰명**을 연결 기준으로 사용한다.
- `tools/audit_catalog_io.py`의 고아 산출 37건은 부분문자열·느슨한 이름 연결을 허용하는
  **어휘 감사 기준**이다.
- 따라서 정확일치는 실행계약·dependencies·외부입력의 기준으로 유지하고, 부분일치는
  `name_drift_candidate` 또는 `loose_match_audit`로 별도 표기한다.
- 두 수치를 한 개의 `orphan` 지표로 합치지 않는다.

### 2.2 별칭 상태

`entity-alias-registry.json`에는 6건이 있으며, 4건은 `proposed`, 2건은 `needs_decision`이다.
아직 `confirmed` 별칭은 없으므로 토큰 보고서의 249개·외부 입력 147개를 자동으로 줄이지 않는다.
별칭 확정은 별도 자격자 결정으로 처리한다.

---

## 3. 회의 판정 및 후속조치

### 3.1 IR-01 — 항목별 확인 질문 부재

**판정:** 중대 발견을 채택한다. 질문의 존재와 검토 가능성은 다른 조건이다.

**후속조치:** 보고서 생성기를 다음 개정에서 항목별 질문으로 변경한다.

- 미션: 미산출·외부 입력, 확정된 모호성, Gate, risk class, 출력별 증거를 질문에 반영한다.
- 토큰: `external_input`, `output_only`, 별칭 후보, 단위 후보, 생산·소비 미션 문맥을 질문에
  반영한다.
- 공통 질문은 문서 머리말에 두고, 항목별 질문은 해당 항목의 차이만 적는다.

**상태:** `implementation_candidate`  
**담당:** PMO + report generator owner  
**승인 한계:** 질문 생성 규칙의 적용은 보고서 품질 조치이며, 미션·토큰의 도메인 의미를
승인하는 것이 아니다.

### 3.2 IR-02 — 전 항목 동일 판정

**판정:** 중대 발견을 채택한다. 단일 `recommended_disposition`은 우선순위를 제공하지 않는다.

**후속조치:** 다음 개정에 승인 상태가 아닌 `preflight_tier`를 추가한다.

| 등급 | 의미 | 기준 후보 |
|---|---|---|
| `machine_preflight_pass` | 구조·정합성 점검 통과; 승인 아님 | 정본 대조·참조·필드 검사가 통과하고 별도 경보가 없음 |
| `contract_clarification_required` | 계약·어휘를 먼저 정리해야 함 | 외부 입력, 미산출 입력, 명명 드리프트, 별칭 후보, 단위 미정 |
| `qualified_judgment_required` | 분야 자격자 판정 없이는 진행하지 않음 | risk C/D, 안전·법규·계통·시운전 Gate, DR 안건 대상 |

현재는 이 등급을 계산해 승인으로 표시하지 않는다. 각 등급의 실제 건수는 재생성 시점의
정본·별칭 상태에서 다시 계산한다.

**상태:** `implementation_candidate`  
**담당:** PMO + Mission owners  
**승인 한계:** `machine_preflight_pass`도 `approved`·`baselined`가 아니다.

### 3.3 IR-03 — 고아 산출 수치 이원화

**판정:** 기준을 분리해 해소한다.

**결정 제안:**

1. 실행계약·dependencies·`external_input`은 정확일치를 정본 기준으로 한다.
2. 부분문자열·유사명 연결은 자동 연결하지 않고 `name_drift_candidate`로 보고한다.
3. `audit_catalog_io.py`와 토큰 보고서는 두 기준을 각각 명시해 같은 이름의 수치를 혼용하지 않는다.
4. F-07에는 `exact_unlinked_outputs`와 `loose_match_orphan_outputs`를 별도 필드로 기록한다.

**상태:** `proposed_for_governance_approval`  
**담당:** PMO + Chief Engineer + Data Lead  
**승인 필요:** 엔티티 사전의 기준 어휘 정책. 승인 전에는 어느 수치도 도메인 계약 확정으로
해석하지 않는다.

### 3.4 IR-04~IR-07 — 타입·단위·한계·별칭

| 안건 | 회의 판정 | 후속조치 | 상태 |
|---|---|---|---|
| IR-04 타입 신뢰도 | 토큰명만으로 high를 만들지 않는다 | 소비 미션 문맥·생산 미션 출력·기존 스키마 근거를 후보 근거에 추가 | `implementation_candidate` |
| IR-05 단위 공백 | 수치형 토큰을 먼저 분리한다 | `common.schema.json`·H2 공식·계산기 인자 정의를 우선 조회하고 근거 위치를 기록 | `implementation_candidate` |
| IR-06 동일 한계 | 항목별 한계를 생성한다 | 외부입력·산출·결정·수량·별칭 후보별로 다른 한계 문구 생성 | `implementation_candidate` |
| IR-07 별칭 분리 | 별칭 등록부를 우선 참조한다 | `proposed/needs_decision`은 보고만 하고 `confirmed`만 재생성에 반영 | `implementation_candidate` |

---

## 4. 도메인 소견의 2차 판정

아래 항목은 보고서의 소견을 사실로 자동 승인하지 않고, 저장소 내부 근거로 재현 가능한
계약 위험과 자격자 결정이 필요한 질문을 분리한 것이다.

### 4.1 즉시 수정 후보 — 생성 규칙 또는 근거 연결

#### DR-04 — 단위 제안의 접두어 오분류

`FireLoad`, `PowerPrice`, `PowerReadyDecision`, `PowerSpec`, `PowerBlockOption`은 토큰명
접두어 또는 부분문자열만으로 수량 단위가 붙은 사례다. 이 소견은 현재 보고서 생성 규칙에서
재현된다.

**조치 제안:** 소비 미션의 입력 용도와 기존 저장소 타입을 먼저 조회한다. 특히 `FireLoad`는
화재안전 기준 레코드, `PowerPrice`는 가격 레코드, `PowerReadyDecision`은 결정 레코드,
`PowerSpec`·`PowerBlockOption`은 구조화 레코드 후보로 분리한다.

**보류:** 수정 후에도 해당 토큰의 최종 JSON Schema와 단위는 분야 owner가 승인하기 전까지
기준선으로 승격하지 않는다.

#### DR-05 — 저장소 확정 정의 우선 사용

다음은 저장소 내부 정의가 있으므로 토큰명만으로 제안하지 말고 근거를 표시해야 한다.

- `Coordinate`·`CoordinateRef`·`Coordinates`: `schemas/common.schema.json`의 coordinate 정의
- `Autonomy`: `app/calc.py`의 `autonomy_days` 사용
- `Pressure`: `app/calc.py`의 `storage_pressure_bar_abs` 사용
- `quantity`: `unit`과 `basis`를 함께 요구하는 공통 계약

이 값들을 곧바로 모든 미션의 계약 승인으로 확대하지 않는다. 저장소 정의가 적용되는 문맥과
토큰의 실제 소비 미션이 일치하는지 확인해야 한다.

### 4.2 자격자 결정 필요 — 자동 수정 금지

| 안건 | 보류 이유 | 필요한 결정 |
|---|---|---|
| DR-01 M-059/065/066 | ICSS 안전개념의 최소 위험분석 수준이 정본에 없다 | HSE/Process/ICSS가 M-059의 개념 범위와 HAZID·HAZOP/LOPA 선행조건을 결정 |
| DR-02 M-087/088/089 | 수소 투입 전 통제의 미션 산출·승인 주체가 없다 | Commissioning/HSE가 불활성화·잔류 산소 측정·투입 승인 Evidence와 산출 미션을 결정 |
| DR-03 M-055 | 위험구역 분류 입력에 누출률 또는 시나리오 집합이 없다 | HSE/Process가 누출률 계약·계산 실행 ID·적용 범위를 결정 |
| DR-06 M-050 | `PreconsultationResult`의 G2 충분성이 정의되지 않았다 | Electrical/Grid owner가 계통운영자 회신의 필수성·대체근거·조건부 통과 기준을 결정 |
| DR-07 M-067 | 모델 유효범위 검사가 완료기준에 없다 | HSE owner가 모델 범위·입력 범위 이탈 시 차단조건을 결정 |
| DR-08 `LeakCases` | HAZID 별칭인지 외부 시나리오인지 불명확 | HSE가 `LeakCases`의 producer/alias/source를 결정 |
| DR-09 M-048 | 전력품질 검토현상 목록과 적용판이 없다 | Electrical/Grid가 `GridRules` 기준의 검토현상 목록을 결정 |
| DR-10 `Purity` | 순도와 불순물별 농도 계약 분리가 필요할 수 있음 | Hydrogen/Process owner가 적용 품질기준과 단위·불순물 목록을 결정 |

위 안건은 회의록이 답을 대신하지 않는다. 결정 전에는 해당 미션·토큰을
`qualified_judgment_required`로 취급하고 Gate 기준선에 사용하지 않는다.

---

## 5. 조치 목록

| 조치 ID | 대상 | 조치 | 담당 역할 | 선행조건 | 상태 |
|---|---|---|---|---|---|
| ACT-D034-01 | IR-01 | 항목별 질문 생성 규칙과 재생성 | PMO + generator owner | 없음 | Proposed |
| ACT-D034-02 | IR-02 | 3단계 `preflight_tier` 계산 추가 | PMO + Mission owners | IR-03 기준 분리 | Proposed |
| ACT-D034-03 | IR-03 | 정확일치·부분일치 지표 분리 및 F-07 용어 정리 | PMO + Chief Engineer + Data Lead | 엔티티 어휘 정책 | Proposed |
| ACT-D034-04 | IR-04/05/06 | 문맥·저장소 근거·항목별 한계로 보고서 재생성 | Data/AI + domain leads | source precedence | Proposed |
| ACT-D034-05 | IR-07 | alias registry의 `confirmed`만 파생본에 반영 | PMO + domain owners | 6건 별칭 결정 | Proposed |
| ACT-D034-06 | DR-04/05 | 단위 생성 규칙의 오분류 제거 및 근거 위치 추가 | Data/AI + Chief Engineer | 없음 | Proposed |
| ACT-D034-07 | DR-01/02/03 | 안전 입력·수소 투입·누출률 계약 자격자 결정 | HSE/Process/ICSS/Commissioning | 회의 소집 | Hold |
| ACT-D034-08 | DR-06/07/08/09/10 | 계통·모델·누출·전력품질·수소품질 계약 결정 | 해당 domain owners | Evidence/기준 확인 | Hold |

---

## 6. Gate와 기준선 판정

- D-034 보고서: `proposed_not_approved` 유지
- 100개 미션: owner 승인 0건, 기준선 승격 0건
- 249개 토큰: 의미 타입·단위·근거 요건 승인 0건, 기준선 승격 0건
- DR-01~DR-03: 안전 관련 입력 공백으로 해당 미션 계약은 `HOLD` 성격으로 취급
- 실제 Gate 통과에는 Evidence 레코드, source/version/hash, required evidence 대조,
  Gate audit, 지정 인간 승인 서명이 모두 필요

F-02는 미해소다. 이번 회의록은 검토 순서와 보류 사유를 구체화했지만, 미션·토큰의
도메인 계약을 승인하지 않았다.

---

## 7. 회의록 한계

- 이 문서는 구조·계약 검토와 후속조치 회의록이며, 안전성·인허가 적합성·SIL·안전거리·
  수소품질 표준 적합성을 판정하지 않는다.
- 법령·기술기준 원문이 `metadata_only`인 항목은 조문번호·판번호·시행일을 확정하지 않는다.
- DR-01~DR-03 및 DR-06~DR-10은 질문과 결정대상만 정리했으며, 자격자 답변이 없다.
- `proposed`·`Hold`는 승인·거부가 아니라 후속 검토 상태다.
- 이 회의록 작성 시점에는 관련 변경을 커밋·푸시하지 않는다. 별도 제출 커밋에서 파일과
  결정 로그 반영분을 확인해야 한다.

---

## 8. 도메인 검토 보충 제출 확인

2026-09-23 커밋 `6c529d5`로 `independent-review-D-034.md`에 새로운 도메인 검토가
제출되었다. 이는 기존 2차 회의록의 DR 안건을 대체하지 않고, 다음 근거와 범위를 가진
보충 견해로 접수한다.

- 검토 범위: 공정안전·계통·시운전 관련 미션 13건과 단위 후보 33건
- 중대 소견: DR-01~DR-04 4건
- 보통·경미 소견: DR-05~DR-10 6건
- 근거 범위: 저장소 내부 확정 사실과 분야 일반 실무 순서
- 제외 범위: 법령·KGS 조문·코드번호·판번호·시행일, 안전거리·SIL·인허가 적합성·화염길이
- 결정 상태: 전건 제안. `owner_decision`·`decision_ref`·인간 서명 없음

### 8.1 접수 판정

| 구분 | 2차 회의록과의 관계 | 접수 결과 |
|---|---|---|
| DR-01·DR-02·DR-03 | 안전 판정에 필요한 입력 계약 공백 | 기존 `HOLD` 안건을 구체화함 |
| DR-04 | 단위 후보 생성 규칙의 오분류 | 기계적 재생성 후보를 구체화함 |
| DR-05 | 저장소 확정 정의 미활용 | 근거 우선순위 조치를 구체화함 |
| DR-06~DR-10 | 계통·모델·별칭·전력품질·수소품질 검토 | 자격자 결정 대상을 구체화함 |

따라서 `6c529d5`의 새 견해는 2차 회의록에 **보충 제출된 것으로 확인**한다. 다만 이
접수는 사실·소견의 기록이며, 미션 순서 변경·입력 추가·단위 확정·별칭 확정 또는 Gate
통과를 의미하지 않는다. 해당 변경은 표의 담당 자격자가 별도 결정 ID와 Evidence로 승인해야 한다.
