# Forge H2 Enterprise 문서 지도

이 폴더는 사람이 읽는 프로젝트 문서의 정본입니다. AI Agent는 먼저 [프로젝트 헌장](00-project/project-charter.md)과 루트의 [스키마 레지스트리](../schemas/registry.json)를 읽습니다.

## 00 — 프로젝트 기준

- [project-charter.md](00-project/project-charter.md): 프로젝트 경계·목표·정본 문서·Agent 시작 규칙
- [progress.md](00-project/progress.md): 누적 진행 기록

## 01 — 제품·도메인

- [hydrogen-power-ai.md](01-product/hydrogen-power-ai.md): 수소발전소 전문 시스템 정의
- [product-strategy.md](01-product/product-strategy.md): 제품 원칙과 사용 경험 방향

## 02 — 엔지니어링

- [coding-model-design.md](02-engineering/coding-model-design.md): 코딩 모델과 Agent 실행 루프 설계

## 03 — 프로젝트 거버넌스

- [pm-plan.md](03-governance/pm-plan.md): 조직·역할·RACI·게이트·변경관리
- [requirements-baseline.md](03-governance/requirements-baseline.md): 제품 요구사항과 수용조건
- [mission-catalog.md](03-governance/mission-catalog.md): 함수형 미션과 실행계약
- [evidence-standard.md](03-governance/evidence-standard.md): 근거 등급과 데이터 계보
- [gate-criteria.md](03-governance/gate-criteria.md): G0–G7 승인 기준
- [risk-register.md](03-governance/risk-register.md): 프로젝트 리스크
- [decision-log.md](03-governance/decision-log.md): 기준선 변경과 의사결정 누적 기록

## 04 — Agent·전문가 운영

- [agent-operating-model.md](04-agent-system/agent-operating-model.md): Agent 권한·독립성·호출 규칙
- [expert-agent-catalog.md](04-agent-system/expert-agent-catalog.md): 기술사급 기술전문가와 재무·법무 자문단
- [meeting-protocol.md](04-agent-system/meeting-protocol.md): Agent 의견을 듣고 결정하는 회의 프로토콜
- [process-agent-map.md](04-agent-system/process-agent-map.md): M-001–M-100 단계별 호출 흐름
- [international-expert-organization.md](04-agent-system/international-expert-organization.md): 국제 프로젝트의 8개 전문가 Council과 국제 Agent 오버레이
- [agents/registry.json](../agents/registry.json): AI가 읽는 전체 Agent 레지스트리
- [agents/international-overlay.json](../agents/international-overlay.json): 국제 프로젝트용 추가 Agent·Council·게이트 조건
- [workflow/process-agent-map.json](../workflow/process-agent-map.json): AI가 읽는 단계별 실행 맵
- [report1-easy.md](../reports/report1-easy.md): 비전문가용 설명 보고서
- [report2-technical.md](../reports/report2-technical.md): 전문지식용 기술 보고서
- [knowledge/README.md](../knowledge/README.md): Professional 정의와 지식 DB 파이프라인

## 파일명 규칙

- 문서는 소문자 `kebab-case.md`를 사용한다.
- 폴더 앞의 숫자는 Agent와 사람이 읽는 우선순위·문서 영역을 나타낸다.
- 스키마 파일은 API 계약이므로 `schemas/`에서 별도로 관리한다.
- 실행 코드는 `app/`, 모델 실험은 `forge_model/`, 누적 데이터는 `data/`에 둔다.
