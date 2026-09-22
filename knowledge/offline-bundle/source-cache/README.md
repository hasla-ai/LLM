# Offline Source Pack

이 디렉터리는 인터넷이 없는 환경에서 사용할 법규·표준·계약·금융·허가 근거의 로컬 보관 위치다.

원문은 프로젝트의 라이선스와 관할에 맞게 적법하게 반입해야 한다. 표준 전문을 임의로 생성하거나 웹 페이지 요약만으로 대체하지 않는다.

반입 절차:

1. 해당 문서의 현행 판본과 적용 관할을 확인한다.
2. 라이선스가 허용하는 PDF·HTML·문서 파일을 이 디렉터리에 저장한다.
3. `knowledge/offline-source-register.json`의 해당 `knowledge_id`에 `local_artifact`, `revision`, `sha256`을 등록한다.
4. `python -m knowledge.pipeline offline-check`를 실행한다.
5. `baseline_ready: true`가 된 뒤에만 해당 근거를 Gate·Decision 기준선으로 사용한다.
6. `python -m knowledge.pipeline build-offline-bundle`로 해시 번들을 다시 만든다.

현재 일부 항목에는 공식 공개 범위·초록·가이드 페이지가 캐시되어 있다. 그러나 ISO·IEC·NFPA·KGS 표준, FIDIC 계약조건 등 전체 라이선스 원문이 없는 항목은 계속 `metadata-only`로 유지한다. 공개 페이지 캐시는 참고·추적용이며, 오프라인 기준선 승격을 허용하지 않는다.
