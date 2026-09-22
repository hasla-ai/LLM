# Forge H2 수소 계산 커널 기준선

문서 ID: FHZ-CALC-KERNEL-001  
Jira Epic: SCRUM-29  
보호 이슈: SCRUM-39  
상태: controlled_overlay

## 1. 역할

계산 커널은 수소발전소의 반복 계산을 결정론적으로 수행하는 실행층이다. 기존 SCRUM-18의 프로젝트·미션·Evidence·G0–G7 순서를 변경하지 않는다. 커널은 숫자를 생성하는 LLM이 아니라, 검증된 입력과 등록된 수식으로 계산 결과를 만드는 도구다.

```text
ProjectIntent / Evidence
  → 단위·차원·범위 검증
  → Calculation Kernel
  → Quantity + 불확실도 + 근거 계보
  → 전문 Agent 검토
  → Gate Evidence / Decision
```

## 2. Quantity 계약

모든 계산값은 숫자 하나가 아니라 다음 객체다.

```json
{
  "quantity_id": "Q-H2-FLOW-001",
  "value_si": 1250.0,
  "si_unit": "kg/s",
  "dimension": {"M": 1, "L": 0, "T": -1, "I": 0, "Th": 0, "N": 0, "J": 0, "A": 0},
  "display": {"value": 4500.0, "unit": "kg/h"},
  "uncertainty": {"distribution": "normal", "stddev_si": 25.0, "p10_si": 1218.0, "p50_si": 1250.0, "p90_si": 1282.0},
  "reliability_tier": "T4",
  "evidence_ids": ["EVD-EXAMPLE-001"],
  "assumption_ids": [],
  "status": "calculated"
}
```

규칙:

1. 차원 불일치 덧셈·뺄셈은 경고가 아니라 `BLOCKED`다.
2. 입력 하나가 T5이면 그 입력을 사용하는 결과의 신뢰도는 T5보다 높아질 수 없다.
3. 입력·수식·계산기 버전·실행 ID·Evidence를 계산서에 연결한다.
4. 평균만 저장하지 않고 필요한 경우 P10/P50/P90과 분포 가정을 저장한다.
5. 계산 결과는 설계 적합성·안전거리·SIL·인허가 적합성 판정이 아니다.

## 3. 프로젝트 흐름 연결

| 기존 흐름 | 커널 사용 | 결과 | 최종 검토 |
|---|---|---|---|
| G1 사업성·수요 | 발전량·운전시간·CAPEX/OPEX·민감도 | 사업성 계산서 | Finance + Sponsor |
| G2 수소·발전·계통 | 수소량·저장·압축·보조전력·성능·계통량 | 설계기초 계산서 | Chief Engineer + 분야 Agent |
| G3 안전·인허가 | 방출·유틸리티·환경 입력의 정량화 | 안전·허가 검토 입력 | HSE/Regulatory + 자격자 |
| G4 FEED·EPC | 물량·비용·공기·성능보증 입력 | FEED/견적 근거 | EPC + Finance + Independent Reviewer |
| G6/G7 | 성능시험·운영 KPI·정비 기준 | 시험·인수 계산서 | Commissioning + Operations |

커널 실행은 해당 미션의 `MissionRun`과 연결되어야 하며, Evidence 없는 계산서는 Gate 기준선으로 승격하지 않는다.

## 4. 실행·보호 원칙

- 언어모델은 숫자와 수식을 임의로 만들지 않는다.
- 허용된 Python 표현식과 단위검사만 실행한다. 동적 코드 실행은 금지한다.
- 일반 공식은 `knowledge/formula-library.json`, 수소플랜트 고유 18식은 `knowledge/formula-library-h2.json`에 저장하고, H2 도메인 연결은 `knowledge/calculation-kernel.json`에서 관리한다.
- H2 고유식은 현재 `machine_checked` 단계다. 출처 문헌·판번호·시행일·전문가 검증 전에는 T1 또는 설계 기준선으로 승격하지 않는다.
- 커널·스키마·수식 변경은 SCRUM-39 보호 루틴과 PMO Change Request를 통과해야 한다.
- 기존 G0–G7, Evidence 의미, 인간 승인, 오프라인 `deny_all_remote_fetch` 규칙을 우회하는 변경은 금지한다.

## 5. 완료 조건

각 커널 작업은 입력·출력 JSON, 차원검사, 검증사례, 실패조건, calculator_version, Evidence 연결, 사람 검토자를 남겨야 한다. 계산이 실행되었다는 사실만으로 설계 승인이나 건설 지시가 되지 않는다.
