# CLAUDE.md

Forge H2 Enterprise — 프로젝트 ID `FHZ-ENTERPRISE-001`
수소연료전지 발전소 건설·운영을 회사형 PMO와 전문 Agent 체계로 실행하는 저장소.

PM 도구: Jira `SCRUM` (hangrock.atlassian.net)

---

## 1. 절대 규칙

이 프로젝트는 인허가와 안전이 걸린 실제 발전소 사업이다. 아래는 협상 대상이 아니다.

1. **법령·기준을 기억으로 인용하지 않는다.** 법령명까지는 후보로 제시할 수 있으나
   조문번호·KGS 코드번호·판번호·시행일은 검색·확인 없이 쓰지 않는다. 확인 못 하면
   빈칸으로 두고 "검증 필요"로 표시한다. 틀린 조문은 없는 것보다 나쁘다.
2. **언어모델이 숫자를 만들지 않는다.** 모든 수치는 코드가 계산한다.
   `knowledge/formula-library-h2.json` 의 공식을 쓰고, 없으면 공식을 먼저 등록한다.
3. **근거 없는 값은 하류를 오염시킨다.** 값에는 항상 출처와 근거등급이 붙는다.
   결과의 등급은 기여한 입력 중 가장 나쁜 등급이다.
4. **화염길이·안전거리·SIL·인허가 적합성은 계산하지 않는다.** 누출률까지만 낸다.
   그 앞은 검증된 상관식 근거와 자격자 판정이 있어야 한다.
5. **추정값을 기준선으로 승격하지 않는다.** 가정은 가정 레지스터에 만료일과 함께 남긴다.

## 2. 근거등급 (schemas/evidence.schema.json 의 reliability_tier)

| 등급 | 뜻 |
|---|---|
| T0 | 관청·법령 확인, 정의값 |
| T1 | 기술기준 조항 (판번호 확인됨) |
| T2 | 시험성적서·실측 |
| T3 | 벤더 자료 |
| T4 | 유도 계산·현장조사 |
| T5 | 가정 |
| — | 근거 없음 (발행 차단) |

내장 상수는 T4 로 시작한다. 발행기관·판번호·시행일을 붙여야 T1 으로 올린다.

## 3. 저장소 지도

```
docs/00-project/      헌장, 진행기록
docs/01-product/      제품 전략
docs/02-engineering/  h2-calc-kernel.md — 계산 커널 설계
                      h2-calc-kernel-overlay.md — SCRUM-29 controlled_overlay 기준선
docs/03-governance/   pm-plan, mission-catalog, gate-criteria, evidence-standard,
                      risk-register, decision-log, findings-2026-09-22.md
docs/04-agent-system/ Agent 운영·전문가 카탈로그·회의 프로토콜
schemas/              JSON Schema 정본 (mission-definition, mission-run, evidence,
                      gate, formula-library, decision, meeting, change-request …)
knowledge/            catalog.json, agent-databases/, formula-library.json,
                      formula-library-h2.json, offline-bundle/
workflow/             process-agent-map.json — M-001~M-100 Agent 라우팅
agents/               registry.json, international-overlay.json
app/                  FastAPI + SQLite. main.py, calc.py, static/
tools/                validate_formulas.py
forge_model/          로컬 코딩모델 학습 (legacy_prototype)
```

## 4. 검증

변경 후 반드시 실행한다.

```
python tools/validate_formulas.py
```

기대: 검증 케이스 실패 0, 스키마 실패 0.
스키마가 0건으로 나오면 `pip install jsonschema` 로 켠다.

새 공식을 추가하면 `validation_cases` 를 반드시 채운다. expected 는 표현식을 실제로
평가해서 넣고 손으로 계산한 값을 넣지 않는다. 검증 케이스 없는 공식은 설계 근거가 못 된다.

## 5. 미해소 결함 — 작업 전 확인

`docs/03-governance/findings-2026-09-22.md` 참조.

| ID | 내용 | Jira |
|---|---|---|
| F-01 | 단계 분류가 mission-catalog.md / process-agent-map.json / mission-definition.schema.json 세 파일에서 다르다. M-041~M-060 의 20개가 잘못된 Agent 로 라우팅된다. **다른 미션 작업의 선행조건.** | SCRUM-34 |
| F-02 | mission-catalog.md 가 mission-definition.schema.json 의 필수 필드(dependencies, completion_criteria, block_conditions)를 갖고 있지 않다. | — |
| F-03 | app/main.py 의 계산 결함 4건. 수정 모듈은 app/calc.py 에 있고 교체는 미완. | SCRUM-35 |
| F-05 | 기존 공식 15개 중 14개에 validation_cases 가 없다. CI 없음. | SCRUM-36 |

**F-01 이 풀리기 전에는 미션 정의를 스키마 충족 상태로 쓰지 않는다.** 어떤 phase 값을
넣어도 세 문서 중 둘과 어긋난다.

## 6. app/main.py 계산 결함 (F-03)

`/api/mvp/feasibility` 에서 확인된 것. `app/calc.py` 가 고쳤고 교체는 별도 작업이다.

- LHV `33.33` 이 코드에 하드코딩. 정확값 33.322 kWh/kg. 공식 라이브러리에서 와야 한다.
- `power_mw` 가 총발전단인지 순출력인지 정의 없음. 소내부하가 모델에 없어 순출력을
  넣으면 수소량이 5~12% 과소산정.
- 저장 산정에 사용가능 잔압 비율 없음. 15~30% 과소산정.
- `storage_density_kg_m3 = 30.0` 은 약 450~500 bar 에 해당. 200 bar / 288 K / Z=1.10
  에서 실제는 약 15.3 kg/m³.

## 7. 교차 검증 기준값

브라우저 커널(`app/static/h2-module.html`)과 `app/calc.py` 는 독립 구현이다.
같은 입력에 같은 값을 내야 한다. 둘이 어긋나면 회귀다.

입력: 20 MW(총발전단), η 47.5% LHV, 소내부하 7.8%, 이용률 90%

| 항목 | 값 |
|---|---|
| 수소 소비량 | 1,263.59 kg/h |
| 순출력 | 18.44 MW |
| 연간 수소 | 9,962 t/yr |
| 저장밀도 (200 bar, 288.15 K, Z 1.10) | 15.3 kg/m³ |

## 8. 작업 방식

- 커밋 메시지는 한국어. 무엇을 왜 바꿨는지와 검증 결과를 본문에 남긴다.
- 기준선 문서(`docs/03-governance/`)를 바꾸면 `decision-log.md` 에 사유를 남긴다.
- 기존 `app/`·`forge_model/`·`data/` 는 `legacy_prototype` 으로 보존한다. 삭제하지 않는다.
- Jira `SCRUM` 에 대응 이슈가 있으면 커밋 메시지에 키를 적는다.
- 확신이 없으면 값을 만들어 채우지 말고 빈칸과 "확인 필요"를 남긴다.

## 9. Jira 매핑

| 키 | 내용 |
|---|---|
| SCRUM-18 | 에픽 — 수소발전소 건설 프로그램 |
| SCRUM-19~26 | G0~G7 게이트 작업 |
| SCRUM-29 | 에픽 — 수소 계산 커널 (기술개발) |
| SCRUM-30~33 | 커널 구현 (완료) |
| SCRUM-34 | F-01 단계 분류 불일치 — 선행조건 |
| SCRUM-35 | F-03 app/main.py 교체 |
| SCRUM-36 | F-05 검증 러너 CI 연결 |
| SCRUM-37 | 계산서를 Evidence 로 등록 |
| SCRUM-38 | 커널 Python 이식 |

---

계산이 맞다는 것과 설계가 맞다는 것은 다르다.
안전거리·SIL·인허가 적합성의 최종 판정은 유자격자만 한다.
