from fastapi import FastAPI

from fastapi_pagination import add_pagination

from app.api.v1.api import api_v1
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)
add_pagination(app)
# API 라우터
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
