# Forge H2 의사결정 로그

모든 범위·기술·안전·법규·계약·AI 권한 결정은 이 문서에 누적한다. 취소된 결정도 삭제하지 않고 상태를 `Superseded`로 바꾼다.

## 결정 상태

- `Proposed`: 안건 제안
- `Under Review`: 전문 검토 중
- `Approved`: 기준선에 반영
- `Rejected`: 채택하지 않음
- `Superseded`: 후속 결정으로 대체

## 초기 기준선 결정

| ID | 일자 | 결정 | 이유 | 영향 | 승인자 | 상태 |
|---|---|---|---|---|---|---|
| D-001 | 2026-09-17 | 대한민국을 기본 관할로 삼고 실제 사업지역에서 법규를 재확정한다. | 사용자·프로젝트의 현재 기준 | 법규·인허가 커넥터 설계 | Sponsor + Regulatory | Approved |
| D-002 | 2026-09-17 | Forge H2의 목표는 완전 자동 승인 시스템이 아니라 인간 승인형 엔지니어링 코파일럿이다. | 안전·법적 책임 분리 | 모든 고위험 미션에 HUMAN_REVIEW 적용 | Sponsor + HSE | Approved |
| D-003 | 2026-09-17 | 딸깍 실행은 미션 오케스트레이션이며, 누락 입력을 우회하지 않는다. | 실제 프로젝트의 불확실성 관리 | BLOCKED 상태와 보완요청 필요 | PMO + Product | Approved |
| D-004 | 2026-09-17 | 반복 계산은 결정론적 코드로 만들고 LLM은 해석·계획·문서 초안에 사용한다. | 재현성과 감사 가능성 | 계산기와 LLM 모듈 분리 | Chief Engineer + AI Lead | Approved |
| D-005 | 2026-09-17 | 모든 AI 고위험 출력은 Evidence ID와 검토자를 요구한다. | 출처 없는 법규·수치 차단 | Evidence Gate 적용 | HSE + Data | Approved |
| D-006 | 2026-09-17 | G0–G7 단계 게이트를 통과하지 않은 결과는 다음 기준선으로 승격하지 않는다. | 조기 설계 확정 방지 | Gate Engine 구현 | PMO + Chief Engineer | Approved |
| D-007 | 2026-09-17 | 기존 Forge H2 화면은 폐기하지 않고, 새 Mission/Evidence/Gate 코어의 UI 셸로 전환한다. | 기존 작업 보존·점진적 전환 | 마이그레이션 계획 필요 | Product + Platform | Approved |
| D-008 | 2026-09-17 | 실제 건설 프로젝트 착수 전 Shadow Mode로 AI 결과를 전문 검토자와 비교한다. | 초기 AI 오류의 현장 영향 차단 | 평가셋·검토 로그 필요 | AI Safety + PMO | Approved |
| D-009 | 2026-09-17 | PM 조직의 의사결정권자, 기술사급 전문분야, 재무·법무 자문을 역할형 Agent로 등록하고 미션별로 호출한다. | 회사의 워크로드를 반복 가능한 실행 계약으로 만들기 | Agent registry·process map·호출 로그 필요 | PMO + Chief Engineer | Proposed |
| D-010 | 2026-09-17 | 모든 Agent 의견은 독립적으로 수집하고, 충돌·고위험·게이트·C3 이상 변경은 결정회의를 거친다. | 다수결식 누락과 조용한 진행 방지 | Meeting·Decision 스키마와 human signoff 필요 | PMO + HSE + Independent Reviewer | Proposed |
| D-011 | 2026-09-17 | 대한민국 기술사·법무·재무 자격은 Agent에게 부여하지 않고 실제 담당자의 자격 검증 필드로 관리한다. | AI가 법정 책임자처럼 오인되는 위험 차단 | 전문가 카탈로그와 자격 확인 절차 필요 | HSE + Legal Advisory | Proposed |
| D-012 | 2026-09-17 | 국제 프로젝트는 국내 기본 조직에 International Program·Owner's Engineer·Lender's Technical Advisor·현지 법정기술자·인증·E&S·계약·무역·데이터 Council을 오버레이한다. | 국가·금융·계약·표준·현지 책임 차이 통제 | 국제 Agent overlay와 Council별 게이트 검토 필요 | Sponsor + PMO + Chief Engineer | Proposed |
| D-013 | 2026-09-17 | 국제표준은 수원국 법규·허가·계약·금융조건의 적용성을 확인한 뒤 Standards Applicability Matrix에 등록한다. | 표준을 법규처럼 오인하는 위험 방지 | 표준판·적용조항·차이·책임자·근거 기록 | Chief Engineer + HSE + Local Authority | Proposed |
| D-014 | 2026-09-17 | 모든 Agent는 전문분야·관할·프로젝트 단계에 맞는 Knowledge Entry를 검색하고 출처·판본·검증상태를 함께 반환한다. | 기억·일반검색 의존과 근거 없는 생성 차단 | Knowledge Registry·SQLite·Retrieval Result 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-015 | 2026-09-17 | Professional은 AI가 아니라 자격·경험·범위·권한·독립성·책임·최신성 검증을 갖춘 실제 사람으로 정의한다. | 법정 책임과 AI 보조역할 분리 | Professional Profile과 인간 서명 필수 | Chief Engineer + HSE + PMO | Proposed |
| D-016 | 2026-09-17 | 중앙 Source Catalog를 진실의 원장으로 두고, 각 Agent 전문지식 DB는 읽기 전용 materialized view로 생성하며 모든 Agent가 필요한 범위에서 다른 Agent DB를 읽을 수 있게 한다. | Agent별 전문성 분리와 공통 출처 보존을 동시에 달성 | 중앙 등록·개정·검증 후 Agent DB 재생성, 교차조회 audit 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-017 | 2026-09-17 | 모든 Knowledge Entry의 canonical 저장형식은 JSON으로 통일하고, SQLite는 JSON 원장에서 생성되는 삭제 가능한 파생 검색 인덱스로만 사용한다. | AI·사람·다른 Agent가 동일한 구조화 원장을 직접 읽고 검토할 수 있게 함 | JSON Schema 검증과 재생성 파이프라인 필요 | Data Lead + AI Safety + PMO | Proposed |
| D-018 | 2026-09-17 | 기술사·전공서적 카탈로그와 공식은 JSON 구조로 저장하고, 사용자가 제공했으나 출처·판본이 확정되지 않은 항목은 `user_provided`·`unverified`로 표시한다. | 사서 Agent가 참조할 수 있으면서 공식 기준으로 오인되지 않게 함 | 전문인 검증·단위검사·판본확인 전에는 기준선 승격 금지 | Data Lead + Chief Engineer + AI Safety | Proposed |
| D-019 | 2026-09-17 | 인터넷 단절 시 원격 출처를 조회하지 않고, 해시가 확인된 로컬 source artifact만 기준선 근거로 허용한다. metadata-only 자료는 참고로 반환하되 baseline 승격을 차단한다. | 오프라인에서도 추적성과 안전 통제를 유지 | 라이선스 문서·현행 법규·표준·계약 원문을 source pack으로 반입해야 함 | PMO + HSE + Data Lead + Legal | Proposed |
| D-020 | 2026-09-17 | 오프라인 수소발전소 건설 준비도는 출처뿐 아니라 GIS·계통·수소공급·기상·공학모델·EPC·운영·로컬 실행환경의 자료완전성을 함께 평가한다. | 지식 DB만 있고 실제 설계 입력이 없는 상태 방지 | `offline-requirements.json`의 누락 요구사항은 해당 Gate를 차단 | PMO + Chief Engineer + Data Lead | Proposed |
| D-021 | 2026-09-22 | G0는 필수 출처 원문·ProjectIntent 실제 입력·승인 기록이 확보될 때까지 `HOLD`로 유지한다. | 현재 offline-check 결과 `baseline_ready=false`이고 승인자가 아직 서명하지 않음 | G1 착수 보류, source pack·ProjectIntent·G0 검토회의 필요 | PMO + Chief Engineer + HSE + Data | Under Review |
| D-022 | 2026-09-22 | SCRUM-29 계산 커널과 SCRUM-39 코드 보호는 기존 SCRUM-18·G0–G7의 순서·의미·Evidence 구조를 변경하지 않는 교차 절단 통제로 편입한다. | 계산 재현성과 기존 프로그램 보호를 동시에 확보해야 함 | G1/G2/G3/G4/G6/G7 계산 미션과 모든 릴리스·변경 검토에 영향 | PMO + Chief Engineer + AI/Platform + Cybersecurity | Under Review |
| D-023 | 2026-09-22 | 다른 Agent가 작성한 SCRUM-29 후보 산출물은 canonical 경로로 추가하되 `app/main.py`와 기존 SCRUM-18 실행흐름은 교체하지 않는다. | 계산 결함·공식 검증을 반영하면서 기존 프로그램 불변 원칙을 지켜야 함 | H2 공식 라이브러리·독립 계산 모듈·검증 러너·F-01/F-02 결함 해결 순서 | Chief Engineer + PMO + AI/Platform | Under Review |
| D-024 | 2026-09-23 | 단계(phase) 분류의 정본은 `docs/03-governance/mission-catalog.md`로 하고, `schemas/mission-definition.schema.json`의 phase enum과 `workflow/process-agent-map.json`의 단계별 미션 배정·Gate를 카탈로그에 맞춘다. 카탈로그에 없는 `commissioning` 단계는 제거하고 해당 Agent·산출물·차단조건을 `construction`으로 흡수한다. | 카탈로그만이 100개 미션 전건의 ID·함수·입력·출력·담당·Gate를 한 표에 갖고 있어 다른 두 파일이 카탈로그에서 파생될 수 있다. 역방향은 불가능하다. 또한 스키마 enum은 이미 카탈로그의 10단계와 이름·순서가 일치했으므로 카탈로그 채택 시 변경량이 가장 작다. | workflow 맵 35건 불일치 해소, 미션 100개 전건의 Agent 라우팅 정정, `concept_design` 단계 신설, F-01 종결. F-02 미션 속성 이식과 SCRUM-34 착수 가능 | PMO + Chief Engineer | Approved |
| D-025 | 2026-09-23 | `mission-library-100.json` 을 미션 속성 이식 원본으로 쓰지 않고 참고 자료로만 남긴다. 미션 정의는 정본 카탈로그에서 생성하고, 기계로 도출할 수 없는 필드는 자격자가 작성한다. | 두 문서는 서로 다른 100개 미션 분해다. 산출물 엔티티가 대응하는 미션이 100건 중 3건뿐이고 단계·게이트 구성(G0~G9 COD 종료 vs G0~G7 운영 포함)이 다르다. ID 를 맞춰 병합하면 97개 미션에 틀린 선행관계·완료기준·차단조건이 들어간다. | F-02 해소 경로 변경. `mission-definitions.draft.json` 100건 생성(스키마 100/100·내용완결 0/100), 모호한 선행관계 29건과 100개 미션의 완료기준·차단조건은 자격자 작성 대기 | PMO + Chief Engineer | Approved |
| D-028 | 2026-09-23 | 미션 선행관계 모호 입력 29건을 제안값으로 전건 확정한다. 적용 규칙은 R1 단계교차(다른 단계 산출물은 그 단계의 종결·게이트 미션에 건다), R2 단계내(해당 엔티티를 실제 산출한 미션에 건다), R3 단위(`Intent` 는 정규화 이후 M-002 를 쓴다). | `dependencies` 는 데이터 흐름이 아니라 선행조건 계약이므로 단계 종결 미션에 거는 것이 게이트 통제와 일치한다. 확신이 낮은 8건(M-006·M-031·M-040·M-041·M-049·M-050·M-051·M-053)도 승인했으나 각 항목에 반론을 남겨 재검토 가능하게 했다. | 선행관계 73→100건(66개 미션), 모호 29→0건. 미션 라우팅 DAG 확정. F-02 의 완료기준·차단조건 작성 착수 가능 | PMO + Chief Engineer | Approved |

| D-026 | 2026-09-23 | `/api/mvp/feasibility` 는 기존 응답의 `derived` 키를 유지하면서 `app/calc.py` 결정론적 계산 커널을 호출한다. `power_mw`는 총발전단으로 정의하고, 소내부하·사용가능 저장비율·압력/온도/Z 기반 저장밀도를 계산에 반영한다. 공급사 저장밀도는 명시적 override일 때만 허용한다. | 기존 API 소비자를 깨뜨리지 않으면서 F-03의 하드코딩·총/순출력 혼동·잔압 누락·무근거 저장밀도 문제를 제거해야 함 | F-03 해소, 계산 결과의 공식·가정·근거등급 추적, 3건 회귀 테스트 추가 | Chief Engineer + AI/Platform | Approved |
| D-027 | 2026-09-23 | 공식·스키마 검증, 회귀 테스트, 단계 정합성, 미션 정의 골격, 보호 감사를 Python 3.11·3.12 GitHub Actions CI에서 실행한다. 보호 감사는 실패 시 비정상 종료한다. 기존 공식 14개에 대표 validation case를 추가하고 안전 평가 목록에 `sum`·`zip`을 허용한다. | 검증이 로컬 실행자의 기억에 의존하면 회귀와 보호정책 위반이 배포 전에 잡히지 않음 | F-05 해소, `requirements-dev.txt`와 `.github/workflows/quality.yml` 추가, 공식 15개 전부 검증 케이스 보유 | PMO + AI/Platform | Approved |

| D-029 | 2026-09-23 | M-046이 `PreconsultationResult`와 `PreliminarySLD`를 함께 산출하고, M-047은 `PreliminarySLD`로 계통연계 검토를 수행하며, M-058은 Phase 5에서 `DetailedSLD`를 산출한다. | 예비 단선도로 G2 계통연계 검토를 시작하고 G3에서 상세 단선도로 확정하는 실무 반복을 표현한다. 새 미션 ID를 삽입하지 않아 100개 미션·단계·Gate 계약을 보존한다. | M-046/M-047/M-058/M-060 입출력 계약과 P05/P06 산출물 명칭 변경. M-047 선행관계 1건 추가, 전방참조 1건 제거. 예비 SLD는 G2 검토용이며 최종 설계 기준선이 아니다. | PMO + Chief Engineer | Approved |

| D-030 | 2026-09-23 | 100개 미션의 목적·완료기준·차단조건을 `mission-content-draft.json`에 카탈로그의 함수·입력·출력·담당·Gate만 근거로 초안 작성하고, 생성기가 이를 `mission-definitions.draft.json`에 병합한다. | `mission-library-100.json`은 카탈로그와 다른 미션 분해이므로 이식 원본으로 사용하지 않는다(D-025). 내용 초안은 미션 실행계약의 출발점이지만 자격자 검토 전에는 기준선이 아니다. | 목적·완료기준·차단조건 100/100 작성. 입력·출력 schema_ref와 output quality_checks는 별도 작성 대기. 미션별 owner 검토와 Gate 증거 기준 확인 필요. | Mission owners + PMO | Under Review |

| D-031 | 2026-09-23 | 100개 미션의 입력·출력 `schema_ref`와 출력 `quality_checks`를 `mission-contract-draft.json`에 작성하고 생성 정의에 병합한다. 참조는 계약 원장의 논리 위치를 가리키며, 실제 JSON Schema 등록과 자격자 검토 전에는 초안으로 유지한다. | 전체 미션 계약의 TODO를 제거하되 도메인별 JSON Schema를 임의로 발명하지 않고, 카탈로그 입출력과 검토 가능한 계약 원장을 먼저 고정한다. | schema_ref 200건·quality_checks 100건 작성, 미션 정의 스키마 100/100·내용 완결 100/100. 실제 스키마 승격·owner 검토·Gate 증거 확인이 다음 작업이다. | Mission owners + PMO | Under Review |

| D-032 | 2026-09-23 | 카탈로그의 100개 미션 입력·출력 토큰을 `schemas/mission-contracts.schema.json`의 200개 draft `$defs`로 등록하고, `registry.json`에 추가한다. 각 미션의 담당자·Gate·검토범위를 `mission-owner-review-queue.json`에 `pending`으로 생성한다. | 도메인 타입·단위·근거 요건을 추측해 완성한 것으로 표시하지 않고, 현재 단계에서는 필수 필드 존재 계약과 검토 대상을 먼저 등록한다. | schema_ref 200건 등록·참조 검사 200/200, owner 검토 큐 100건 생성. 값의 도메인 타입 구체화, 담당자 승인, Gate 증거 검토는 미완료이며 기준선 승격을 차단한다. | Mission owners + PMO | Under Review |
| D-033 | 2026-09-23 | 카탈로그의 입출력 토큰을 고유 토큰별 도메인 계약 검토 큐로 분리하고, 생산·소비 미션과 단계·Gate를 함께 기록한다. 타입·단위·널 허용·근거 요건·스키마 형태는 자격자 검토 전까지 비워 둔다. | 100개 미션의 200개 필드 존재 계약만으로는 실행 가능한 도메인 계약이 되지 않는다. 그러나 토큰 의미를 추측하면 F-07의 명명 드리프트와 잘못된 라우팅을 기준선에 넣을 수 있으므로, 카탈로그에서 확인되는 연결관계만 기계적으로 고정한다. | `entity-contract-review-queue.json`에 고유 토큰 249건(산출 토큰 102건·외부 입력 147건)을 `pending_owner_review`로 등록. 도메인 타입·단위·근거 요건·owner 승인·Gate 증거 확인은 미완료이며 기준선 승격을 차단한다. | Mission owners + domain leads + PMO | Under Review |
| D-034 | 2026-09-23 | 100개 미션과 249개 도메인 토큰 각각에 대해 제안 판정·근거·Gate 증거·검토 질문·한계를 포함한 자격자 검토 보고서를 생성한다. 보고서의 모든 결정값은 `proposed_not_approved`로 두고 승인·서명은 별도 결정 기록으로만 반영한다. | 초안 완결 수치만 제시하면 자격자가 무엇을 승인해야 하는지와 어떤 불확실성이 남았는지 확인하기 어렵다. 반대로 토큰 타입·단위를 자동 확정하면 F-07의 명명 드리프트와 잘못된 설계 계약을 기준선에 넣을 위험이 있다. | 미션 보고서 100건과 토큰 보고서 249건 생성. 미션별 목적·완료기준·차단조건·품질검사·Gate 증거 제안·한계, 토큰별 후보 타입·단위·근거 요건·신뢰도·한계를 포함한다. 자격자 결정·Evidence·Gate audit·인간 서명은 미완료다. | Mission owners + domain leads + PMO | Under Review |
| D-035 | 2026-09-23 | D-034 독립검토 2차 회의록에 따라 보고서 검토 우선순위를 기계적 preflight와 자격자 판단으로 분리하고, 정확일치를 실행계약 기준으로 유지하며 부분일치는 명명 드리프트 감사로 분리한다. IR-01·IR-02·IR-04·IR-05·IR-06·IR-07과 DR-04·DR-05는 재생성 조치 후보로, DR-01·DR-02·DR-03·DR-06·DR-07·DR-08·DR-09·DR-10은 자격자 결정 전 HOLD 안건으로 기록한다. | 전 항목 동일 질문·판정은 검토 우선순위를 만들지 못하고, 정확일치와 부분일치 수치를 한 지표로 섞으면 엔티티 사전 범위가 달라진다. 안전·계통·시운전 입력 공백과 단위 오분류를 자동 승인하지 않고, 기계적 조치와 사람의 도메인 결정을 분리해야 한다. | `independent-review-D-034-2nd-meeting.md` 제출. 보고서·토큰·안전계약은 아직 승인·기준선 승격하지 않으며, 3단계 preflight·항목별 질문·근거 우선순위·별칭 상태 연결·단위 규칙 개선을 후속조치로 등록한다. | PMO + Chief Engineer + HSE/Process + Electrical/Grid + Commissioning + domain owners | Under Review |
| D-036 | 2026-09-23 | 커밋 `6c529d5`로 제출된 공정안전·계통·시운전 도메인 검토(DR-01~DR-10)를 D-035 2차 회의록의 보충 견해로 접수한다. DR-01·02·03은 안전 입력계약 `HOLD`, DR-04·05는 기계적 재생성 후보, DR-06~10은 자격자 결정 대상으로 유지한다. | 새 검토는 13개 미션·33개 단위 후보를 대상으로 하며 저장소 내부 확정 사실과 일반 실무 순서만 사용했다. 조문·KGS 코드·판번호·안전거리·SIL·인허가 적합성·화염길이는 판정하지 않았고 모든 소견은 제안이다. | `independent-review-D-034-2nd-meeting.md` 8절에 보충 제출을 기록. 접수는 변경 승인이나 Gate 통과가 아니며, 미션 순서·입력·단위·별칭 변경은 별도 결정 ID·Evidence·인간 서명이 필요하다. | HSE/Process + Electrical/Grid + Commissioning + Chief Engineer + PMO | Under Review |
| D-037 | 2026-09-23 | 법령·기술기준의 **서지사항 확인**에 한해 온라인 조회(WebSearch/WebFetch)를 사용하고, 결과를 `knowledge/verified-citations.json` 에 기록한다. 서지 확인은 Evidence 가 아니며 원문(local_artifact)과 sha256 없이는 `baseline_eligible` 이 될 수 없다. `tools/check_citations.py` 가 이를 강제한다. | CLAUDE.md 1절 1항은 조문번호·판번호·시행일을 '검색·확인 없이' 쓰지 말라고 한다. 확인 수단이 없어 그동안 빈칸으로 두었다. 확인 경로를 열되 D-019(해시된 로컬 artifact 만 기준선 근거)를 훼손하지 않도록 서지 확인과 원문 확보를 분리한다. `deny_all_remote_fetch` 는 에이전트 런타임 정책이므로 변경하지 않는다. | ISO 14687 현행판(2025, 2판)·KGS AH371·AH171 개정일 확인. KGS 상세기준 PDF 가 공개 제공되는 정황이 있어 KNW-KR-KGS-CODE 의 metadata_only 전제 재확인 필요 | PMO + Chief Engineer + HSE/Regulatory | Approved |
| D-038 | 2026-09-23 | D-037의 서지 확인을 미션·도메인 토큰·Gate의 적용 후보로 연결하고, 현행판 재확인 대상을 별도 큐로 관리한다. | 연결은 적용성·적합성 승인이나 Evidence 승격이 아니다. 자격자가 원문과 프로젝트 경계를 검토해야 하며, AH371·AH171·FU671은 최신 관찰값이 D-037 기록과 달라질 수 있어 갱신 보류로 남긴다. | `citation-application-review-queue.json` 4건, 후보 미션·토큰·Gate 연결, `owner_decision=0`, `baseline_eligible=false` | PMO + Qualified Domain Owners | Proposed |
| D-039 | 2026-09-23 | KGS AH371 은 본 프로젝트에 **적용하지 않는다.** 원문 1.1.1 의 적용범위가 연료소비량 232.6 ㎾ 이하인 소용량 고정형 연료전지이고 본 프로젝트는 연료투입 약 42 MW 다. 또한 이 코드 원문 PDF 를 저장소에 반입하지 않는다. | 원문 76쪽을 직접 확인해 적용범위 조문·제개정이력·근거 법령을 대조했다. 추정이 아니라 조문 대조 결과다. 반입 보류 사유는 h2hub 저작권 정책상 공공누리 표시가 없는 자료의 복제·배포가 금지되고 이 PDF 에 표시가 없기 때문이다. | `verified-citations.json` CIT-KGS-AH371 갱신(applicability=not_applicable, import_status=rejected). **본 프로젝트 규모에 적용되는 KGS 코드는 아직 미확인이며 M-062 map_kgs_codes 의 선행 과제로 남는다.** 추측하지 않는다 | Chief Engineer + HSE/Regulatory | Approved |

## 의사결정 기록 양식

새 결정은 아래 형식으로 추가한다.

```markdown
| D-XXX | YYYY-MM-DD | 한 문장 결정 | 대안과 선택 이유 | 비용·일정·안전·법규 영향 | 승인자 | Proposed |
```

상세 안건은 아래 항목을 추가로 기록한다.

- 문제와 결정이 필요한 기한
- 검토한 대안
- 입력자료와 Evidence ID
- 각 분야의 반대 의견
- 안전·법규·계통 영향
- 결정으로 변경되는 미션과 문서
- 재검토 조건
- 승인자의 이름·역할·시각

### D-029 상세 의미와 적용 범위

- `PreliminarySLD`는 계통연계점, 전압, 발전기·변압기·버스 구성, 보호·계측 경계,
  Dispatch 기준, 개정번호를 포함하는 **G2 검토용 예비 산출물**이다.
- M-047의 `GridStudyPackage`가 예비 SLD의 수정 필요성을 발견하면 M-046과 M-047을
  해당 개정으로 재실행한다. 이를 M-058의 선행조건으로 만들지 않는다.
- `DetailedSLD`는 M-050의 `PowerReadyDecision` 이후 M-058에서 생성하며, M-060의
  개념설계 패키지 검토에 사용한다. 예비 SLD와 상세 SLD를 동일 문서 상태로 취급하지 않는다.
- 이 결정은 Phase 4에 11번째 미션을 추가한다는 뜻이 아니다. 100개 미션과 기존 ID를
  유지하기 위해 M-046의 출력 계약을 확장한 것이다.
- 다음 조건이면 D-029를 재검토한다: 계통운영자가 G2에서 최종 SLD를 요구하는 경우,
  예비 SLD만으로 보호협조·연계검토가 성립하지 않는 경우, 또는 상세 SLD가 G2 Gate
  증거로 요구되는 경우.

## 미해결 안건

| ID | 안건 | 필요한 입력 | 담당 | 기한 | 상태 |
|---|---|---|---|---|---|
| A-001 | 첫 실증 프로젝트의 발전방식과 규모 확정 | 수요·수소공급·부지 후보 | Sponsor + Chief Engineer | TBD | Proposed |
| A-002 | 외부 GIS·법규·계통 데이터 공급원 선정 | API·라이선스·갱신주기 | Data Lead | TBD | Proposed |
| A-003 | 독립 안전·인허가 검토기관 선정 | 후보·계약범위·예산 | HSE Authority | TBD | Proposed |
| A-004 | Mission 1–10의 JSON Schema 승인 | 스키마 초안·예시 입력 | Product + PMO | TBD | Proposed |
| A-005 | Shadow Mode에 사용할 과거 설계 프로젝트 선정 | 비식별 문서·검토자 | AI Safety Lead | TBD | Proposed |
| A-006 | SCRUM-29 커널 9개 하위 작업의 실제 구현 브랜치·검증사례·담당자 확정 | SCRUM-30–38 구현 산출물·브랜치·테스트 | Chief Engineer + AI/Platform | TBD | Proposed |
| A-007 | SCRUM-39 보호정책의 저장소 권한·비밀관리·감사로그 운영수단 확정 | 조직 저장소·실행환경·권한 매트릭스 | Cybersecurity + PMO | TBD | Proposed |
