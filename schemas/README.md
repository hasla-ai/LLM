# Forge H2 Canonical Schemas

이 디렉터리는 Forge H2의 **단일 정본(canonical contract)** 이다. FastAPI, TypeScript, 다른 Agent, LLM 프롬프트는 이 스키마를 기준으로 데이터를 주고받는다.

## 설계 원칙

1. 필드명은 영문 `snake_case`를 사용한다.
2. 사람이 읽을 수 있도록 모든 핵심 필드에 `title`, `description`, `examples`를 둔다.
3. AI가 추측하지 않도록 미정 값은 가능한 경우 `null`로 명시한다.
4. 단위가 있는 수치는 숫자만 저장하지 않고 `value`와 `unit`을 함께 저장한다.
5. 모든 실행 결과는 `status`, `evidence_ids`, `assumptions`, `blockers`를 가진다.
6. 안전·법규·시공 관련 결과는 `human_review` 또는 `blocked` 상태를 거쳐야 한다.
7. 스키마에 없는 임의 필드는 만들지 않는다. 확장이 필요하면 `extensions` 안에 둔다.
8. 기존 필드의 의미를 바꾸지 않는다. 변경은 `schema_version`을 올리고 마이그레이션을 만든다.
9. 배열의 항목은 식별 가능한 ID를 갖게 한다.
10. 출력은 설명문이 아니라 검증 가능한 JSON 객체로 반환한다.

## 파일 순서

| 파일 | 목적 | 주 사용자 |
|---|---|---|
| `registry.json` | 모든 계약의 색인과 실행 순서 | Agent/개발자 |
| `common.schema.json` | 공통 ID·상태·좌표·단위·근거 타입 | 모든 Agent |
| `project-intent.schema.json` | 사업주가 제공하는 최초 요구사항 | Intake Agent |
| `mission-definition.schema.json` | 함수형 미션의 계약 | Orchestrator Agent |
| `mission-run.schema.json` | 미션 1회 실행 결과 | Executor/Review Agent |
| `quantity.schema.json` | SI 값·차원·불확실도·근거를 가진 계산값 | Calculation Kernel/Engineering Agent |
| `calculation-kernel.schema.json` | 결정론적 계산 커널 정책과 미션 연결 | Chief Engineer/Data Lead |
| `evidence.schema.json` | 근거·출처·버전·검증 상태 | Evidence Agent |
| `gate.schema.json` | G0–G7 승인 게이트 | PMO/Review Agent |
| `change-request.schema.json` | 설계·요구·법규·계약 변경 | PMO/Change Agent |
| `agent-definition.schema.json` | Agent의 역할·자격 기대치·권한·협의 계약 | Agent Registry |
| `agent-invocation.schema.json` | Agent 호출·의견·차단·인간검토 기록 | Orchestrator Agent |
| `meeting.schema.json` | Agent 의견·이견·결정·액션 회의 기록 | PMO/Meeting Agent |
| `decision.schema.json` | 근거·의견·인간 서명을 연결한 결정 | Decision Agent |
| `professional-profile.schema.json` | 실제 전문가의 자격·경험·권한·독립성 | PMO/Reviewer |
| `knowledge-entry.schema.json` | 출처·판본·관할·검증을 가진 지식 단위 | Knowledge Agent |
| `retrieval-request.schema.json` | Agent·단계·관할이 포함된 검색 요청 | Orchestrator Agent |
| `retrieval-result.schema.json` | 검색 결과와 출처·검증 추적 | Knowledge Agent |
| `examples/` | 사람이 읽는 최소 유효 예시 | 모든 사용자 |

## Agent 사용 규칙

```text
1. registry.json을 먼저 읽는다.
2. 입력 JSON을 해당 schema로 검증한다.
3. 모르는 값은 추측하지 말고 null + blockers에 기록한다.
4. 계산값은 calculator_version과 input_snapshot을 기록한다.
5. 법규·안전·시공 판단은 evidence_ids와 reviewer가 없으면 human_review로 둔다.
6. 기존 실행 결과를 덮어쓰지 말고 새 run_id를 생성한다.
7. 다음 미션은 next_mission_ids에 명시한다.
8. 결과가 기준선으로 승격되는 것은 Gate가 승인할 때뿐이다.
9. 현재 미션의 Agent는 `agents/registry.json`과 `workflow/process-agent-map.json`에서 선택한다.
```

## 검증 명령

JSON 문법 검증:

```powershell
python -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('schemas').rglob('*.json')]; print('schemas: ok')"
```

스키마를 수정할 때는 예시 파일도 함께 갱신하고, `schema_version`과 변경 이유를 `docs/03-governance/decision-log.md`에 기록한다.
