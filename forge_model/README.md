# Forge Code Model

이 폴더는 Forge AI의 코딩 모델을 직접 학습하기 위한 최소 파이프라인이다.

## 1. 데이터셋 만들기

```powershell
& "C:\Users\hrjeo\anaconda3\envs\dl\python.exe" -m forge_model.prepare_dataset --root . --out data/forge_code.jsonl
```

처음에는 현재 저장소의 Python 코드만 사용한다. 실제 학습 데이터로 확장할 때는 라이선스가 확인된 저장소와 자체 작성 코드를 추가해야 한다.

## 2. 작은 모델 학습

```powershell
& "C:\Users\hrjeo\anaconda3\envs\dl\python.exe" -m forge_model.train --data data/forge_code.jsonl --steps 1000
```

이 구현은 이해와 검증을 위한 작은 문자 단위 causal Transformer다. 품질을 높이려면 이후 BPE tokenizer, 더 큰 데이터셋, GPU 학습, 평가셋, LoRA/사전학습 모델로 확장한다.

## 데이터 원칙

- 라이선스가 확인된 코드만 사용한다.
- 비밀키, `.env`, 개인정보, 빌드 산출물은 제외한다.
- 중복·자동 생성물·깨진 파일을 제거한다.
- 학습 데이터와 평가 데이터를 저장소 단위로 분리한다.
