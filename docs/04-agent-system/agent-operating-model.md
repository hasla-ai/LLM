# Forge H2 Enterprise Agent 운영모델

## 1. 목적

Forge H2 Enterprise의 Agent는 프로그램 개발을 위한 챗봇 목록이 아니라, 수소발전소 건설·시운전·운영 프로젝트를 실제 회사의 워크로드처럼 수행하기 위한 역할 단위다.

각 Agent는 다음을 반드시 가진다.

1. 담당 미션과 입력
2. 출력 계약과 품질조건
3. 협의해야 할 다른 Agent
4. 추천·승인·중지 권한의 경계
5. 요구되는 실제 전문가 자격 수준
6. 인간 검토·서명 조건

## 2. 권한 원칙

```text
Agent 호출
  → 근거·계산·가정 확인
  → 각 전문가 Agent의 독립 의견 수집
  → 충돌·위험·누락 청취
  → 결정 회의
  → 실제 책임자의 인간 승인
  → 기준선 승격
```

AI Agent는 실제 기술사·변호사·사업주·관할기관이 아니다. `approval_scope`는 워크플로에서 결정을 준비하거나 승인 요청을 만들 수 있는 범위이며, 실제 법정 서명권을 부여하지 않는다.

## 3. Agent 종류

| 종류 | 역할 | 기준선 승격 |
|---|---|---|
| `governance` | Sponsor·PMO·Chief Engineer 등 의사결정 구조를 대행 | 인간 승인 필수 |
| `technical` | 설계·안전·시공·운영 전문분야 의견 작성 | 자격자 검토 필수 |
| `advisory` | 금융·법무·계약·보험·지역사회 자문 | 자문 의견으로만 사용 |
| `assurance` | 품질·독립검토·근거·AI 안전성 확인 | 독립성 유지 |
| `platform` | 미션·회의·권한·릴리스 실행 | 기술·안전 결정권 없음 |

## 4. 모든 Agent 호출의 공통 계약

- 호출마다 `CALL-*` ID를 발급한다.
- 호출 목적, 미션·근거·이전 결정 참조를 기록한다.
- 출력은 `proceed`, `proceed_with_conditions`, `hold`, `stop`, `request_more_data`, `no_objection` 중 하나로 표현한다.
- 찬성 의견만 모으지 않는다. 반대·조건·불확실성·미해결 이견을 별도로 기록한다.
- 기술·안전·법무·허가·계약·시공·운영 결과는 인간 검토 없이 `baselined`할 수 없다.
- 근거가 없거나 담당 자격자가 없으면 추측하지 않고 `blocked`로 반환한다.

## 5. 독립성 규칙

1. 설계 작성 Agent는 자기 설계를 단독 승인하지 않는다.
2. EPC·시공 Agent는 품질·안전·독립검토 Agent를 우회하지 않는다.
3. 상업·재무 Agent는 안전·법규 적합성을 승인하지 않는다.
4. AI/Platform Agent는 제품 배포를 승인할 수 있지만 발전소 설계·허가·시공을 승인할 수 없다.
5. Sponsor는 사업 지속·예산·착공·중단을 결정하지만 전문 계산의 정확성을 대신 검증하지 않는다.

## 6. 권한 상태

```text
ADVISORY       의견·초안만 작성
RECOMMEND      선택지와 추천안을 작성
REVIEW         근거·품질·충돌을 검토
APPROVAL_READY 인간 승인 요청을 만들 수 있음
HUMAN_APPROVED 실제 승인 기록이 존재함
BASELINED      다음 미션의 입력으로 승격됨
BLOCKED        추측 없이 작업 중지
```

`HUMAN_APPROVED`가 없는 `APPROVAL_READY` 결과는 다음 단계에서 사용하지 않는다.

## 7. 기준 파일

- 전체 목록: `agents/registry.json`
- 단계별 호출: `workflow/process-agent-map.json`
- 호출 계약: `schemas/agent-invocation.schema.json`
- 회의 계약: `schemas/meeting.schema.json`
- 결정 계약: `schemas/decision.schema.json`
