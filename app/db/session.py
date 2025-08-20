from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # 커밋 후 객체 접근시 다시 SELECT 방지(선호)
)

def get_db() -> Generator[Session, None, None]:
    """DB 세션"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()