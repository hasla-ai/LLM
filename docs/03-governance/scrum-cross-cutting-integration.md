# SCRUM-29 · SCRUM-39 교차 절단 통합 기준선

## 1. 목적

이 문서는 Jira의 기술개발 Epic `SCRUM-29`와 기존 프로그램 보호 작업 `SCRUM-39`를
기존 건설 프로그램 `SCRUM-18`의 G0–G7 흐름에 연결하는 운영 기준선이다.

핵심 원칙은 세 층을 섞지 않는 것이다.

```text
SCRUM-18 / G0–G7        건설 프로젝트의 순서·Gate·승인 권한
SCRUM-29 / SCRUM-30–38  결정론적 계산·수량·불확실도·계산 Evidence
SCRUM-39                코드·스키마·지식·기록을 지키는 보안·변경 통제
```

SCRUM-29와 SCRUM-39는 새 Gate를 만들지 않는다. 기존 Gate의 입력, 차단조건,
Evidence, 변경관리, 인간 승인에 연결되는 교차 절단 통제다.

## 2. 전체 실행 흐름

```text
ProjectIntent / 좌표 / 수요
  → 출처 있는 Evidence 등록·해시·판본 확인
  → 해당 Mission 호출
  → SCRUM-29 계산 커널(단위·차원·불확실도·계보)
  → 전문 Agent의 독립 검토
  → 회의·이견·가정·Decision Log 기록
  → Gate Evidence 패키지 생성
  → 인간 책임자 서명
  → G0–G7 판정 또는 HOLD/REOPEN
  → 오프라인 번들·append-only 기록에 보존
```

LLM은 수치를 발명하지 않는다. 계산 커널은 허용된 결정론적 식만 실행하고,
안전거리·SIL 적정성·허가 적합성·시공 릴리스·상업운전 승인은 판정하지 않는다.

## 3. SCRUM-29 하위 작업의 시스템 연결

| Jira | 책임 | 연결 산출물 | 상태/차단 |
|---|---|---|---|
| SCRUM-30 | 8기본차원·단위 대수 | `schemas/quantity.schema.json`, 커널 단위검사 | 커널 계약에 반영 |
| SCRUM-31 | Evidence 등급 전파·계산 차단 | `knowledge/calculation-kernel.json`, Gate Evidence 규칙 | T5 입력의 승격 금지 |
| SCRUM-32 | 불확실도·Monte Carlo P90 | Quantity uncertainty 계약 | 실제 분포 엔진·검증사례 추가 필요 |
| SCRUM-33 | H2 공식 18개 | `knowledge/formula-library-h2.json` | 22개 케이스 통과, 전문가 검증 전 기준선 금지 |
| SCRUM-34 | Phase 분류 불일치 | `docs/03-governance/findings-2026-09-22.md` | F-01 미해결, ID·Gate 매핑 후 승격 |
| SCRUM-35 | 기존 `app/main.py` 계산 결함 | `app/calc.py` 후보 모듈 | 기존 API는 보존, 별도 통합 승인 필요 |
| SCRUM-36 | CI·공식 검증 | `tools/validate_formulas.py` | 로컬 러너 통과, CI 연결은 후속 |
| SCRUM-37 | 계산표를 Evidence로 보존 | `schemas/quantity.schema.json`, input snapshot 계약 | 실제 Gate 계산표 생성기 필요 |
| SCRUM-38 | Python 커널·실행정책 | `knowledge/calculation-kernel.json`, `app/calc.py` | 동적 코드 금지·인간 검토 강제 |

커널은 G1 사업성, G2 수소·전력·계통, G3 안전·인허가 입력, G4 FEED/EPC,
G6 성능시험, G7 운영 KPI의 계산 미션에 연결된다.

## 4. SCRUM-39 보호 통제

보호 대상은 `app/`, `forge_model/`, `agents/`, `workflow/`, `schemas/`,
`knowledge/`, `docs/03-governance/`, `data/project-records/`다.

보호 루틴은 다음을 읽기 전용으로 검사한다.

- 기존 G0–G7의 존재와 순서, 묵시적 진행 금지
- Evidence의 SHA-256 해시 계약과 Gate 필수 Evidence
- 오프라인 `deny_all_remote_fetch`
- 동적 수식 코드 금지
- H2 공식의 검증 케이스와 기준값의 출처·근거 상태
- 계산 커널의 SCRUM-29 연결, SCRUM-39 보호, 결정론성, 인간 검토
- 작업 트리에 변경이 있으면 별도 변경 검토가 필요한지 여부

보안 감사 로그는 Evidence를 대신하지 않는다. Evidence는 기술·법규·계산의
근거이고, 보안 감사는 그 근거와 프로그램이 무단 변경되지 않았는지를 확인한다.

## 5. Gate별 적용

| Gate | 계산 커널의 역할 | SCRUM-39 통제 |
|---|---|---|
| G0 | 계산 기준선·실행정책을 범위에 등록 | 기존 프로그램·Gate·Evidence 스키마 보존 |
| G1 | 수요·출력·수소량·CAPEX/OPEX 입력의 예비 계산 | 계산기·공식 라이브러리 변경 검토 |
| G2 | 공급량·저장량·계통·면적 입력의 단위/차원 검증 | 코드·공식·스키마 변경 시 재기준선 |
| G3 | 안전·허가에 필요한 계산 입력·불확실도 제공 | 커널이 안전/허가 승인을 대체하지 못하도록 차단 |
| G4 | FEED/EPC 물량·성능·비용 산정의 계산 계보 제공 | 기준선 변경은 CR·회귀시험·인간 검토 필요 |
| G5 | 시공 릴리스는 계산 커널 단독 승인 불가 | IFC·검사·품질 기록 보호 |
| G6 | 성능시험·측정불확도·수소 투입 전 계산 재현 | 계산기 버전·입력 snapshot·Evidence 보존 |
| G7 | 운영 KPI·연간 수소량·성능 기준선 재현 | 운영 기록·OT 보안·감사 기록 보호 |

## 6. 현재 판정

- H2 공식 라이브러리: 18개 공식, 자체 검증 케이스 22개. 전체 공식 검증 러너 결과는 23건 통과, 실패 0건이다.
- 오프라인 번들: 119개 파일, 해시·누락·초과 파일·source register 검증 통과.
- SCRUM-39 보안 감사: 통과. 단, 작업 트리 변경은 검토 대상이다.
- G0: `HOLD`. 7개 Evidence가 아직 `unverified`이고 인간 서명이 대기 중이다.
- 오프라인 기준선: `baseline_ready=false`. 필수 표준·법규 원문 9건이 `metadata_only`다.
- F-01 Phase/ID/Gate 매핑과 F-02 미션 스키마 이식은 아직 해결되지 않았다.

따라서 현재 결과는 “전체 흐름에 구조적으로 연결된 통제 기준선”이지,
실제 발전소 설계·허가·시공 승인이 아니다.

## 7. 기준 파일

- `project.json`
- `workflow/process-agent-map.json`
- `knowledge/calculation-kernel.json`
- `knowledge/formula-library-h2.json`
- `security/protection-policy.json`
- `security/audit.py`
- `docs/03-governance/pm-plan.md`
- `docs/03-governance/requirements-baseline.md`
- `docs/03-governance/decision-log.md`
