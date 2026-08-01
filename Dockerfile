FROM python:3.11-slim

WORKDIR /app

# 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 및 테스트 코드 복사
COPY . .

# PYTHONPATH 명시적 지정 (src 모듈 import 에러 방지)
ENV PYTHONPATH=/app

# pytest 실행을 기본 명령으로 설정
CMD ["pytest", "-v"]