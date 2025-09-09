# uv 공식 이미지 사용 (Python + uv 사전 설치)
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 작업 디렉토리
WORKDIR /app

# 런타임 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# uv 환경 설정 (바이트코드 컴파일로 성능 향상)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 개발 환경 설정 (ARG로 제어 가능)
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}

# 의존성 설치를 위한 파일 복사 (캐시 최적화)
COPY pyproject.toml uv.lock ./

# 의존성 설치 (캐시 마운트 사용)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# 소스 코드 복사
COPY . /app

# 프로젝트 설치 완료
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# 가상환경 PATH 설정
ENV PATH="/app/.venv/bin:$PATH"

# 네트워크 포트 노출
EXPOSE 8000

# uv run으로 애플리케이션 실행 (환경에 따라 reload 조건부)
CMD if [ "$ENVIRONMENT" = "production" ]; then \
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8000; \
    else \
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
    fi
