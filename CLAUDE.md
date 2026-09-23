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
tools/                validate_formulas.py, check_phase_alignment.py,
                      build_mission_definitions.py, check_mission_definitions.py
forge_model/          로컬 코딩모델 학습 (legacy_prototype)
```

## 4. 검증

변경 후 반드시 실행한다.

```
python tools/validate_formulas.py
python tools/check_phase_alignment.py
python tools/check_mission_definitions.py
python -m unittest discover -s tests -v
python -m security.audit
```

기대: 검증 케이스 실패 0, 스키마 실패 0, 단계 불일치 0, 미션정의 불일치 0,
회귀 테스트 실패 0, 보호 감사 실패 0.
스키마가 0건으로 나오면 `pip install jsonschema` 로 켠다.

단계(phase) 분류의 정본은 `docs/03-governance/mission-catalog.md` 다 (D-024).
단계를 바꾸면 카탈로그를 먼저 고치고 `check_phase_alignment.py` 로 나머지 두 파일을 맞춘다.

새 공식을 추가하면 `validation_cases` 를 반드시 채운다. expected 는 표현식을 실제로
평가해서 넣고 손으로 계산한 값을 넣지 않는다. 검증 케이스 없는 공식은 설계 근거가 못 된다.

## 5. 미해소 결함 — 작업 전 확인

`docs/03-governance/findings-2026-09-22.md` 참조.

| ID | 내용 | Jira |
|---|---|---|
| ~~F-01~~ | ~~단계 분류가 세 파일에서 다르다~~ **해소됨 (2026-09-23, D-024).** 카탈로그를 정본으로 삼아 workflow 맵을 v1.1.0 으로 재작성. `check_phase_alignment.py` 가 회귀를 막는다. | SCRUM-34 |
| F-02 | mission-catalog.md 가 스키마 필수 필드를 갖고 있지 않다. 골격 `mission-definitions.draft.json` 생성됨 (스키마 100/100, **내용완결 0/100**). 선행관계 100건 확정(D-028), 100개 미션의 목적·완료기준·차단조건은 자격자 작성 대기. `mission-library-100.json` 은 이식 원본이 아니다 (D-025). | — |
| ~~F-03~~ | ~~app/main.py 의 계산 결함 4건~~ **해소됨 (2026-09-23).** `/api/mvp/feasibility` 가 공식 라이브러리 기반 계산 커널을 호출하고, 총발전단·순출력·사용가능 저장비율·압력/온도/Z 기반 밀도를 반환한다. | SCRUM-35 |
| ~~F-05~~ | ~~기존 공식 15개 중 14개에 validation_cases 가 없다. CI 없음~~ **해소됨 (2026-09-23, D-027).** 공식 15개 모두 validation case를 갖고 CI에서 검증한다. | SCRUM-36 |
| F-06 | 정본 카탈로그에 전방참조가 있다. `M-047`(Phase 4)의 입력 `SLD` 를 `M-058`(Phase 5)이 산출한다. 선행관계로 만들면 순환이 생겨 `forward_references` 로 분리했고 M-047 의 입력 계약은 불완전하다. 자격자 결정 필요. | — |

F-01 이 해소되어 이제 `phase` 값을 스키마대로 쓸 수 있다. 사용 가능한 값은
`intake · business · site · hydrogen · power_grid · concept_design · safety_permit ·
feed_epc · construction · operations` 이며 카탈로그 Phase 0~9 와 1:1 대응한다.
남은 선행조건은 F-02 다. `TODO-AUTHOR` 가 남은 미션 정의는 기준선으로 승격하거나 미션 실행 근거로 쓰지 않는다.

## 6. app/main.py 계산 결함 (F-03) — 해소됨 (2026-09-23)

`/api/mvp/feasibility` 를 `app/calc.py` 계산 커널에 연결했다. 기존 `derived` 응답 키는
유지하고, 계산 근거·가정·신뢰도와 총발전단/순출력 구분을 `calculation` 으로 추가한다.

- LHV는 `knowledge/formula-library-h2.json`의 `reference_values`에서 읽는다.
- `power_mw`는 총발전단으로 명시하고 소내부하율에서 순출력을 파생한다.
- 저장 설치량은 사용가능 저장비율을 반영한다.
- 기본 저장밀도는 압력·온도·압축계수로 계산하며, 공급사 밀도는 명시적 override일 때만 사용한다.
- `tests/test_calc_integration.py`가 API 하위 호환 키와 네 가지 보정값을 회귀 검증한다.

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
| SCRUM-34 | F-01 단계 분류 불일치 — 해소됨 (D-024) |
| ~~SCRUM-35~~ | ~~F-03 app/main.py 교체~~ **해소됨 (2026-09-23, D-026).** |
| ~~SCRUM-36~~ | ~~F-05 검증 러너 CI 연결~~ **해소됨 (2026-09-23, D-027).** |
| SCRUM-37 | 계산서를 Evidence 로 등록 |
| SCRUM-38 | 커널 Python 이식 |

---

계산이 맞다는 것과 설계가 맞다는 것은 다르다.
안전거리·SIL·인허가 적합성의 최종 판정은 유자격자만 한다.
