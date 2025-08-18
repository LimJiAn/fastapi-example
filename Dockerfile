# Python 3.13 슬림 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /workspace

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

ENV PYTHONPATH="/workspace"

# 포트 노출
EXPOSE 8000

# 개발 환경에서 실행 (hot reload 활성화)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]