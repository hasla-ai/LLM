# Forge H2 Enterprise Agent Registry

이 폴더는 수소발전소 건설·운영 프로젝트를 수행하는 역할형 Agent의 정본입니다.

## Agent의 의미

Agent는 실제 사람을 대신하는 독립 법인이 아니라, 다음을 고정한 실행 계약입니다.

- 어떤 전문영역을 담당하는가
- 어떤 입력을 받아 어떤 출력을 내는가
- 누구와 협의해야 하는가
- 어디까지 추천하고 어디서 멈추는가
- 어떤 사람의 검토와 서명이 필요한가

`agents/registry.json`의 Agent는 AI 호출 대상이지만, `professional_engineer_or_equivalent`와 같은 자격 기대치는 실제 담당 전문가를 배정할 때 검증해야 합니다. AI Agent 자체가 기술사 자격을 취득하거나 법정 책임자가 되는 것은 아닙니다.

## 호출 순서

1. `workflow/process-agent-map.json`에서 현재 미션의 주관 Agent와 필수 협의 Agent를 찾는다.
2. 자기 Agent DB를 먼저 검색하고, 필요한 경우 `source_agent_ids`로 다른 Agent DB를 읽는다.
3. 각 Agent를 `schemas/agent-invocation.schema.json`으로 호출하고 의견·근거·차단조건을 기록한다.
4. 의견 충돌, C/D 위험, 게이트, C3 이상 변경이면 `schemas/meeting.schema.json` 회의를 만든다.
5. 회의에서 찬성·조건부·보류·중단 의견을 모두 남긴다.
6. `schemas/decision.schema.json`으로 결정을 기록한다.
7. 실제 자격자·사업주·기관의 인간 승인이 없으면 기준선으로 승격하지 않는다.

## 핵심 파일

- `registry.json`: 전체 Agent 목록과 라우팅 메타데이터
- `international-overlay.json`: 국경간·대주단·현지법·국제계약이 있는 프로젝트의 추가 Agent와 Council
- `../workflow/process-agent-map.json`: M-001~M-100 단계별 호출 계획
- `../schemas/agent-definition.schema.json`: Agent 정의 계약
- `../schemas/agent-invocation.schema.json`: Agent 호출 기록 계약
- `../schemas/meeting.schema.json`: 결정 회의 기록 계약
- `../schemas/decision.schema.json`: 최종 결정 기록 계약
