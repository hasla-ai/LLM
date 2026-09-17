# 미션별 Agent 호출과 프로젝트 진행 순서

기계가 읽는 정본은 `workflow/process-agent-map.json`이다. 이 문서는 사람이 전체 흐름을 빠르게 확인하기 위한 운영판이다.

| 단계 | 미션 | 주관 Agent | 반드시 부르는 전문가 | 결정회의 | 게이트 |
|---|---:|---|---|---|---|
| P01 착수 | M-001–005 | PMO | Sponsor, Product, Chief Engineer, HSE, Data | Gate Review | G0 |
| P02 사업성 | M-006–020 | Finance | Commercial, Hydrogen, Grid, Project Finance, PPA | PMO Integration | G1 |
| P03 부지 | M-021–040 | Survey/GIS | Civil, Geotech, Environment, Logistics, Land/Permit | Design Interface | G1/G2 |
| P04 수소 | M-041–050 | Hydrogen Process | Storage, Mechanical, Piping, Process Safety, HSE | HSE/Regulatory | G2/G3 |
| P05 발전·계통 | M-051–060 | Grid | Electrical, Protection, ICSS, Performance, PPA | Design Interface | G2/G4 |
| P06 안전·허가 | M-061–070 | HSE | Fire, Process Safety, Construction Safety, Electrical Safety, Environment | HSE/Regulatory | G3 |
| P07 FEED·EPC | M-071–080 | EPC | Chief Engineer, Procurement, Commercial, Finance, QA, HSE | Steering Committee | G4/G5 |
| P08 시공 | M-081–088 | Construction | EPC, Construction Safety, Materials/Welding, QA, HSE | PMO Integration | G5/G6 |
| P09 시운전 | M-089–094 | Commissioning | Chief Engineer, Hydrogen, Electrical, ICSS, Process Safety, QA, Operations | Independent Review | G6 |
| P10 운영 | M-095–100 | Operations | Performance, Hydrogen, Process Safety, Cybersecurity, QA | Gate Review | G7 |

## 단계별 실행 계약

각 단계는 다음 6개 결과를 순서대로 남겨야 한다.

1. `lead_agent`의 실행계획
2. `required_agent_ids`의 독립 호출 기록
3. `assurance_agents`의 근거·품질·안전 검토
4. `advisory_agent_ids`의 재무·법무·사업 자문
5. `meeting_id`와 결정·반대의견·조건
6. 인간 승인 후 다음 미션 입력으로 승격된 기준선

Agent를 한 번 호출했다는 사실만으로 미션이 완료되지 않는다. 출력이 미션 계약을 만족하고 회의·승인·근거가 연결되어야 한다.
