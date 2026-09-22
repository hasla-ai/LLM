# Forge H2 근거·데이터 표준

문서 ID: FHZ-DATA-001  
목적: AI와 엔지니어가 사용하는 모든 사실·수치·법규·설계조건의 출처와 유효성을 관리한다.

## 1. 근거 등급

| 등급 | 근거 | 예시 | 사용 제한 |
|---|---|---|---|
| T0 | 관할기관의 공식 원문·허가·검사결과 | 법령 원문, 허가서, 검사필증 | 고위험 기준선 사용 가능, 최신성 확인 필수 |
| T1 | 정부·공공기관·공인 기준기관 | KGS Code, 공공 GIS, 공식 계통회신 | 전문 검토와 버전 확인 후 사용 |
| T2 | 공인시험기관·인증기관 결과 | 성능시험, 재료시험, 교정성적서 | 대상 장비·시험범위 확인 |
| T3 | 제조사·공급사·EPC 자료 | 데이터시트, 보증서, 매뉴얼 | 계약·시험·독립검증 필요 |
| T4 | 사업주·현장·전문가 제공자료 | 수요예측, 현장조사, 회의록 | 출처자와 작성일 기록 |
| T5 | AI 추론·기본값·예비 가정 | 유사사례, 업계 평균, 누락값 추정 | 예비 참고만 가능, 기준선 승격 금지 |

## 2. Evidence 객체

```json
{
  "evidence_id": "EVD-0001",
  "project_id": "FHZ-001",
  "type": "law|standard|drawing|vendor|survey|test|decision|measurement",
  "title": "공식 문서명",
  "source_uri": "https://...",
  "source_owner": "기관·회사·작성자",
  "document_number": "문서번호",
  "revision": "개정번호",
  "issued_at": "2026-01-01T00:00:00Z",
  "effective_from": "2026-01-01",
  "effective_to": null,
  "page_or_location": "p. 12 / sheet P-101 / API response",
  "content_hash": "sha256:...",
  "reliability_tier": "T0",
  "verification_status": "unverified",
  "verified_by": null,
  "verified_at": null,
  "used_by_missions": ["M-061"],
  "supersedes": [],
  "superseded_by": null,
  "notes": ""
}
```

## 3. 근거 상태

- `unverified`: 등록됐지만 담당자가 원문·범위·최신성을 확인하지 않음
- `verified`: 담당자가 출처·내용·적용범위를 확인함
- `conditionally_verified`: 일부 조건에서만 사용 가능
- `superseded`: 새 개정판 또는 새 조사로 대체됨
- `rejected`: 출처·무결성·적용범위 문제로 사용하지 않음
- `expired`: 유효기간 또는 계약기간이 종료됨

## 4. AI 사용 규칙

1. T5 추론은 항상 `assumption`으로 표시한다.
2. 법규·KGS·허가·안전거리 답변은 T0 또는 T1 근거가 없으면 `HUMAN_REVIEW`로 반환한다.
3. 제조사 수치는 T3로 저장하고 계약보증·시험결과와 구분한다.
4. 근거가 여러 개면 우선순위와 충돌을 표시한다.
5. 오래된 근거를 최신 근거처럼 요약하지 않는다.
6. 인용 범위를 페이지·조항·도면번호까지 저장한다.
7. AI가 원문을 변형하면 원문과 생성요약을 분리 저장한다.
8. 증거 없는 숫자는 설계 기준선에 사용할 수 없다.
9. 근거가 삭제되지 않도록 이벤트와 해시를 남긴다.
10. 근거가 대체되면 영향을 받는 미션·문서·게이트를 재검토한다.

## 5. 데이터 품질검사

| 검사 | 입력 | 실패조건 | 조치 |
|---|---|---|---|
| 출처검사 | URI·문서번호 | 접근불가·기관불명 | UNVERIFIED |
| 최신성검사 | 발행·효력일 | 기준일 이후 만료 | EXPIRED |
| 무결성검사 | 콘텐츠 해시 | 파일 변경 | 재등록·검토 |
| 범위검사 | 설비·지역·용량 | 적용범위 불일치 | REJECTED |
| 단위검사 | 수치·단위 | 단위 미상·변환 실패 | BLOCKED |
| 공간검사 | 위도·경도·좌표계 | 좌표계 불명 | BLOCKED |
| 교차검사 | 동종 자료 | 압력·유량·용량 충돌 | REVIEW_REQUIRED |
| 승인검사 | 검토자·권한 | 권한 없는 확인 | UNVERIFIED |

## 6. 데이터 계보

모든 산출물은 아래 링크를 가져야 한다.

```text
Document
 └─ MissionRun
     ├─ InputSnapshot
     │   └─ Evidence IDs
     ├─ Calculator/Model Version
     ├─ Assumption IDs
     ├─ Reviewer/Decision
     └─ OutputSnapshot
```

## 7. 보존과 보안

- 원문 파일은 해시와 함께 보존한다.
- 사업비·계약·개인정보·보안자료는 별도 권한으로 격리한다.
- 법규·설계·계약·안전 근거는 프로젝트 종료 후에도 보존정책에 따라 보관한다.
- 삭제가 필요하면 실제 삭제 대신 보존정책·법적근거·승인자를 기록한다.
- OT 운영 데이터와 AI 학습 데이터는 분리한다.
- 외부 LLM 전송 여부와 전송 필드를 프로젝트별로 설정한다.

## 8. Evidence 완료조건

Evidence는 다음을 모두 만족해야 `verified`가 된다.

- 출처가 확인됨
- 발행일·개정번호·효력범위가 확인됨
- 적용 대상과 프로젝트 조건이 일치함
- 내용 해시가 저장됨
- 담당 검토자가 기록됨
- 사용 미션과 제한사항이 연결됨

## 9. 게이트 검증루틴과 AI 앙상블의 지위

문서 파일의 존재는 Evidence가 아니다. 게이트 승격 전에 `python -m knowledge.pipeline audit-gate`가 다음을 기계적으로 검사한다.

1. 게이트의 `required_evidence_ids`가 비어 있지 않다.
2. 각 Evidence ID에 대응하는 JSON 레코드가 존재한다.
3. `content_hash`가 `sha256:<64자리 hex>` 형식이고 원문 파일의 실제 해시와 일치한다.
4. 출처 소유자·문서번호·판본·페이지/조항/경로가 채워져 있다.
5. 신뢰도 등급과 검증상태가 허용 범위이며, `verified`이면 검토자와 검증시각이 있다.
6. 사용 미션, 제한사항, 관할·적용범위가 연결되어 있다.
7. 조건을 만족한다고 표시한 Entry Condition에도 Evidence ID가 연결되어 있다.

검증루틴이 실패하면 Gate는 `HOLD` 또는 `REOPEN` 상태로 남고, 단순히 문서가 저장소에 있다는 이유로 통과할 수 없다.

OpenAI·Claude·SolarPro 등 여러 AI의 독립 판정은 `AgentInvocation`의 보조 검토자료다. 각 판정은 모델 ID·프롬프트 버전·참조 출처·실행 시각·dissent를 남겨야 하며, 다수결이나 일치 자체는 Evidence 또는 인간 승인을 대체하지 않는다. 최종 Gate Evidence는 출처 검증을 통과한 원문·계산·시험·회의 기록이어야 하고, 최종 결정은 지정된 인간 승인자가 서명한다.
