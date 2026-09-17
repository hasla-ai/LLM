# Forge H2 Enterprise 프로젝트 헌장

문서 ID: FHZ-CHARTER-001  
프로젝트 ID: `FHZ-ENTERPRISE-001`  
프로젝트 상태: `INITIATED`  
기준선 일자: 2026-09-17  
기본 관할: 대한민국. 실제 사업지역 확정 시 관할 프로필을 갱신한다.

## 1. 신규 프로젝트 선언

이 문서부터 현재 작업공간은 기존 Claude-style AI 실험의 연장이 아니라 **Forge H2 Enterprise**라는 별도 프로젝트로 관리한다.

- 기존 `app/`와 초기 UI는 삭제하지 않는다.
- 기존 코드는 `legacy_prototype`으로 보존하며 새 프로젝트의 검증 대상이 될 수 있다.
- 새로운 요구사항·미션·근거·게이트·문서는 `FHZ-ENTERPRISE-001`에 귀속한다.
- 전문분야·재무·법무 Agent는 `agents/registry.json`과 `workflow/process-agent-map.json`에 귀속한다.
- 국제 프로젝트는 `agents/international-overlay.json`과 `docs/04-agent-system/international-expert-organization.md`를 추가 기준선으로 사용한다.
- 다른 Agent는 이 헌장과 `schemas/registry.json`을 먼저 읽는다.
- 프로젝트 기준선 변경은 `docs/03-governance/decision-log.md`에 남긴다.

## 2. 사업 목적

사용자가 전력수요, 부지, 발전용량, 수소공급 조건을 입력하면 Forge H2 Enterprise가 수소발전소의 사업성·입지·수소·발전·계통·안전·인허가·FEED·EPC·시공·시운전·운영 미션을 실행하고, 필요한 문서와 승인요청을 생성한다.

목표는 “AI가 건축허가를 대신한다”가 아니라 다음이다.

> **한 번의 프로젝트 시작으로, 건설 가능한 설계·허가·조달·시공 업무를 근거와 승인 이력까지 연결한다.**

## 3. 프로젝트 결과물

1. 요구사항 기준선
2. 프로젝트 미션 그래프
3. 입지·토지·GIS Evidence Pack
4. 수소 공급·저장·발전·계통 기준선
5. 안전성 검토와 인허가 매트릭스
6. FEED·RFP·EPC·조달 패키지
7. 시공·품질·시운전·인수 패키지
8. 운영·정비·규제 준수 원장
9. 모든 결과의 근거·가정·검토자·결정 이력

## 4. 정본 문서

| 영역 | 정본 |
|---|---|
| 프로젝트 전체 운영 | `docs/03-governance/pm-plan.md` |
| 요구사항 | `docs/03-governance/requirements-baseline.md` |
| 미션 계약 | `docs/03-governance/mission-catalog.md` |
| AI·API 데이터 계약 | `schemas/registry.json` |
| 근거 데이터 | `docs/03-governance/evidence-standard.md`, `schemas/evidence.schema.json` |
| 승인 게이트 | `docs/03-governance/gate-criteria.md`, `schemas/gate.schema.json` |
| 위험 | `docs/03-governance/risk-register.md` |
| 의사결정 | `docs/03-governance/decision-log.md` |
| 프로젝트 진행상태 | `docs/00-project/progress.md` |
| Agent 조직·권한 | `agents/registry.json`, `docs/04-agent-system/agent-operating-model.md` |
| 전문가·자문단 | `docs/04-agent-system/expert-agent-catalog.md` |
| 단계별 Agent 호출 | `workflow/process-agent-map.json`, `docs/04-agent-system/process-agent-map.md` |
| 국제 프로젝트 조직 | `agents/international-overlay.json`, `docs/04-agent-system/international-expert-organization.md` |
| 결정회의 | `schemas/meeting.schema.json`, `docs/04-agent-system/meeting-protocol.md` |

## 5. 초기 기준선

```text
Project ID: FHZ-ENTERPRISE-001
Product: Forge H2 Enterprise
Phase: Requirements and Mission Contract Baseline
Gate: G0 - Project Charter
Decision: INITIATED, not yet approved for actual construction
Legacy code: retained as prototype, not construction-grade software
Canonical schemas: schemas/registry.json
Agent registry: agents/registry.json
Process map: workflow/process-agent-map.json
International overlay: agents/international-overlay.json
```

## 6. 첫 승인 안건

신규 프로젝트가 실제 개발 기준선으로 승격되려면 다음 담당자가 승인해야 한다.

- Sponsor: 사업 목적·예산·책임
- PMO: 범위·WBS·게이트·문서 통제
- Chief Engineer: 기술범위·설계 책임
- HSE/Regulatory Authority: 안전·법규·인허가 경계
- Product Owner: 제품 요구사항·사용자 가치
- AI/Data Lead: 스키마·근거·평가·Agent 계약

승인 전에는 어떤 AI 결과도 실제 IFC 도면·시공 지시·법정 제출문서로 표시하지 않는다.

## 7. 신규 Agent 시작 지침

```text
1. docs/00-project/project-charter.md를 읽는다.
2. schemas/registry.json을 읽는다.
3. docs/03-governance/requirements-baseline.md와 docs/03-governance/mission-catalog.md를 읽는다.
4. agents/registry.json과 workflow/process-agent-map.json에서 담당 Agent와 회의 유형을 찾는다.
5. 국제 조건이면 agents/international-overlay.json의 Council과 게이트 요구사항을 추가한다.
6. 기존 app/ 코드는 legacy_prototype으로 취급한다.
7. 임의의 필드·상태·승인권자를 만들지 않는다.
8. 미정값은 null, 불확실성은 assumptions, 부족한 자료는 blockers에 기록한다.
9. 안전·법규·시공 결과는 human_review 없이 baselined하지 않는다.
10. 코드 변경 전에 해당 문서·스키마·Decision Log를 확인한다.
```
