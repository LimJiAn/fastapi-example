import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.api.v1.api import api_v1
from app.core.config import settings

from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """시작 시 자동 마이그레이션"""
    try:
        logger.info("🔄 데이터베이스 마이그레이션 시작...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ 데이터베이스 마이그레이션 완료")
    except Exception as e:
        logger.warning(f"⚠️ 마이그레이션 스킵: {e}")
    yield
    logger.info("🔄 애플리케이션 종료 중...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)
add_pagination(app)
app.include_router(api_v1, prefix=settings.API_PATH)

# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled in production"
    }

# 헬스체크 엔드포인트
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
