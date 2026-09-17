# Forge H2 Enterprise

신규 프로젝트 `FHZ-ENTERPRISE-001`의 엔지니어링·PM·AI 기준선 저장소입니다.

프로젝트 헌장은 [project-charter.md](docs/00-project/project-charter.md)입니다. 전체 문서 지도는 [docs/README.md](docs/README.md)에서 확인할 수 있습니다. 기존 `app/` 기능은 삭제하지 않고 `legacy_prototype`으로 보존합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000.

## Use a local coding model

Install Ollama, then download a model:

```powershell
ollama pull deepseek-coder
Copy-Item .env.example .env
```

Restart the server. Set `AI_PROVIDER=mock` to return to demo mode.

## Forge H2 예비 설계 흐름

1. `/map`에서 프로젝트 ID를 선택하고 지도에 부지·수소 공급원·저장·발전·계통 지점을 배치합니다.
2. 발전 블록의 용량(MW)은 지도에서 통합 예비검토를 실행할 때 자동 합산됩니다.
3. 연간 운전시간과 수소 공급 방식을 입력하면 프로필이 프로젝트별로 SQLite에 저장됩니다.
4. 통합 예비검토는 발전량·수소 사용량·예비 부지면적을 계산합니다.
5. 설비 사이의 WGS84 직선거리와 연결 총거리를 함께 표시합니다.
6. 누락 설비와 근접 배치 후보는 자동 검토 신호로 표시됩니다.
7. `/tasks`에서 좌표가 전문 분야별 검토 작업으로 변환된 결과를 관리합니다.
8. 지도에서 공간 그래프 JSON과 예비 설계 Markdown을 각각 다운로드할 수 있습니다.
9. 모든 프로젝트 데이터와 변경 이벤트는 삭제하지 않고 누적 보존됩니다.
10. 결과는 예비 검토용이며 자격자의 설계·안전·인허가 검토를 대체하지 않습니다.

## 프로젝트 관리 기준선

- [PM 계획서](docs/03-governance/pm-plan.md): 조직, 역할, 게이트, RACI, 산출물, 변경·품질관리
- [리스크 레지스터](docs/03-governance/risk-register.md): 수소·계통·허가·EPC·AI 리스크
- [의사결정 로그](docs/03-governance/decision-log.md): 프로젝트 기준선과 미해결 안건
- [요구사항 기준선](docs/03-governance/requirements-baseline.md): 제품 기능·권한·품질·수용조건
- [미션 카탈로그](docs/03-governance/mission-catalog.md): 100개 함수형 미션과 실행계약
- [근거·데이터 표준](docs/03-governance/evidence-standard.md): 출처·버전·검증·데이터 계보
- [게이트 판정기준](docs/03-governance/gate-criteria.md): G0–G7 진입·통과·차단조건
- [Canonical Schemas](schemas/README.md): Agent·API·사람이 공유하는 JSON 계약
- [Agent 운영체계](docs/04-agent-system/agent-operating-model.md): 의사결정권자·기술전문가·자문단 Agent 운영
- [전문가·자문단 카탈로그](docs/04-agent-system/expert-agent-catalog.md): 대한민국 기준 기술사급 전문영역과 재무·법무 자문
- [Agent 결정회의 프로토콜](docs/04-agent-system/meeting-protocol.md): 모든 의견·이견·결정·서명 기록 방식
- [Report 1 — 쉬운 설명](reports/report1-easy.md)
- [Report 2 — 전문기술 보고서](reports/report2-technical.md)
- [지식 DB·검색 파이프라인](knowledge/README.md)
