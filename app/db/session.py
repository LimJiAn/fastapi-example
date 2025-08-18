from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,            # 연결 상태 확인
    pool_recycle=300,              # 5분마다 연결 갱신
    future=True,
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,        # 커밋 후 객체 접근시 다시 SELECT 방지(선호)
)

def get_db() -> Generator[Session, None, None]:
    """DB 세션"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()