import logging

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.api.v1.api import api_v1
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)
add_pagination(app)
app.include_router(api_v1, prefix=settings.API_PATH)
