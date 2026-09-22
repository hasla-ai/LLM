# AI Ensemble Gate Policy

문서 ID: FHZ-AI-ENSEMBLE-001  
버전: 1.0

## 목적

OpenAI·Claude·SolarPro 등 서로 다른 모델의 검토를 하나의 판단으로 합치되, AI 일치가 출처 검증이나 인간 승인을 대신하지 못하게 한다.

## 신뢰 모델

```text
모델별 독립 호출
  → 모델·프롬프트·출처·실행시각 기록
  → 주장·조건·이견 분리
  → Evidence 검증
  → 전문 Agent 회의
  → 지정 인간 승인
  → Gate 결정
```

## 필수 기록

각 모델 호출은 `schemas/agent-invocation.schema.json`에 따라 다음을 남긴다.

- `trace.model_id`, `trace.prompt_version`, `trace.source_refs`, `trace.request_id`
- 입력 기준선과 Evidence ID
- 요약, 권고, 신뢰도, 조건, dissent/충돌
- `human_review.required`, 검토자, 상태
- 출력 문서·Decision·Gate와의 연결

Claude 또는 SolarPro의 보고서가 대화·파일·Jira로 들어오면 `external-review` 기록으로 먼저 등록한다. 원문 보고서가 없거나 출처가 없는 요약은 참고 의견으로만 남기고 Gate Evidence로 승격하지 않는다.

## 판정 통합 규칙

| 상황 | 처리 |
|---|---|
| 세 모델이 같은 결론 | 독립 기록을 유지하고 Evidence·사람 검토를 계속함 |
| 모델 간 결론 불일치 | PMO가 회의를 열고 이견·추가자료·재실행 조건을 기록함 |
| 한 모델만 안전·법규 위험을 제기 | 위험을 제거할 때까지 `HOLD` 또는 `HUMAN_REVIEW` |
| 출처가 모델마다 다름 | T0/T1 등급과 적용범위를 먼저 비교함 |
| 모델이 계산값을 생성 | 등록된 수식·입력·단위·검증사례 없이는 기준선 사용 금지 |

AI Ensemble 결과는 `advisory`이며, Gate에서 사용할 수 있는 것은 검증된 원문·시험·조사·계산·회의 Evidence와 지정 인간의 서명이다.
