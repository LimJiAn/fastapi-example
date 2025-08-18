import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base_class import Base


# 테스트용 인메모리 SQLite DB
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """테스트용 데이터베이스 세션"""
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        
    # 테이블 삭제
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture
def mock_user_crud():
    """Mock User CRUD"""
    mock = Mock()
    mock.get_by_email = Mock()
    mock.create_with_password = Mock()
    mock.authenticate = Mock()
    mock.is_active = Mock()
    mock.get = Mock()
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis 세션"""
    mock = Mock()
    mock.create_session = Mock()
    mock.delete_session = Mock()
    mock.get_session = Mock()
    return mock
