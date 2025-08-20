import os
import tempfile
from datetime import datetime
from typing import Generator, Dict, Any
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token, get_password_hash
from app.models import User, Board, Post
from app.db.base_class import Base
from app.redis import session as redis_session


# SQLite 테스트 데이터베이스 설정
SQLITE_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLite용 외래키 제약조건 활성화
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite 외래키 제약조건 활성화."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest.fixture(scope="session")
def db_engine():
    """테스트용 데이터베이스 엔진 생성."""
    return engine


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """테스트용 데이터베이스 세션 생성."""
    # 모든 테이블 생성
    Base.metadata.create_all(bind=db_engine)
    
    # 세션 생성
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 테스트 후 모든 테이블 삭제
        Base.metadata.drop_all(bind=db_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """테스트 클라이언트 생성."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """테스트 사용자 생성."""
    user_data = {
        "fullname": "Test User",
        "email": "test@example.com",
        "password": get_password_hash("testpassword123"),
    }
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_user(db: Session) -> User:
    """다른 테스트 사용자 생성."""
    user_data = {
        "fullname": "Another User",
        "email": "another@example.com",
        "password": get_password_hash("anotherpassword123"),
    }
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="session", autouse=True)
def mock_redis_session():
    """모든 테스트에서 Redis 세션 검증을 전역으로 모킹."""
    with patch('app.redis.session.validate_session') as mock_validate, \
         patch('app.api.v1.deps.validate_session') as mock_deps_validate:
        mock_validate.return_value = True
        mock_deps_validate.return_value = True
        yield


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User) -> TestClient:
    """인증된 테스트 클라이언트 생성."""
    token = create_access_token(data={"user_id": str(test_user.id)})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def test_board(db: Session, test_user: User) -> Board:
    """테스트 게시판 생성."""
    board_data = {
        "name": "테스트 게시판",
        "public": True,
        "owner_id": test_user.id,
    }
    
    board = Board(**board_data)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@pytest.fixture
def another_board(db: Session, another_user: User) -> Board:
    """다른 테스트 게시판 생성."""
    board_data = {
        "name": "다른 게시판",
        "public": False,
        "owner_id": another_user.id,
    }
    
    board = Board(**board_data)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@pytest.fixture
def test_boards(db: Session, test_user: User, another_user: User) -> list[Board]:
    """여러 테스트 게시판 생성."""
    boards = []
    
    # 다른 이름과 소유자로 게시판들 생성
    board_data_list = [
        {"name": "첫번째 게시판", "public": True, "owner_id": test_user.id},
        {"name": "두번째 게시판", "public": True, "owner_id": test_user.id},
        {"name": "세번째 게시판", "public": False, "owner_id": another_user.id},
        {"name": "네번째 게시판", "public": True, "owner_id": another_user.id},
    ]
    
    for board_data in board_data_list:
        board = Board(**board_data)
        db.add(board)
        boards.append(board)
    
    db.commit()
    for board in boards:
        db.refresh(board)
    
    return boards


@pytest.fixture
def test_post(db: Session, test_board: Board, test_user: User) -> Post:
    """테스트 게시글 생성."""
    post_data = {
        "title": "테스트 게시글",
        "content": "테스트 게시글 내용입니다",
        "board_id": test_board.id,
        "owner_id": test_user.id,
    }
    
    post = Post(**post_data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@pytest.fixture
def test_posts(db: Session, test_board: Board, test_user: User, another_user: User) -> list[Post]:
    """여러 테스트 게시글 생성."""
    posts = []
    
    # 다른 제목과 소유자로 게시글들 생성
    post_data_list = [
        {"title": "첫번째 게시글", "content": "첫번째 내용", "board_id": test_board.id, "owner_id": test_user.id},
        {"title": "두번째 게시글", "content": "두번째 내용", "board_id": test_board.id, "owner_id": test_user.id},
        {"title": "세번째 게시글", "content": "세번째 내용", "board_id": test_board.id, "owner_id": another_user.id},
        {"title": "네번째 게시글", "content": "네번째 내용", "board_id": test_board.id, "owner_id": another_user.id},
    ]
    
    for post_data in post_data_list:
        post = Post(**post_data)
        db.add(post)
        posts.append(post)
    
    db.commit()
    for post in posts:
        db.refresh(post)
    
    return posts


@pytest.fixture
def another_user_post(db: Session, test_board: Board, another_user: User) -> Post:
    """다른 사용자가 소유한 테스트 게시글 생성."""
    post_data = {
        "title": "다른 사용자 게시글",
        "content": "다른 사용자가 작성한 게시글 내용",
        "board_id": test_board.id,
        "owner_id": another_user.id,
    }
    
    post = Post(**post_data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """인증 헤더 생성."""
    token = create_access_token(data={"user_id": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_board_data() -> Dict[str, Any]:
    """테스트용 샘플 게시판 데이터."""
    return {
        "name": "샘플 게시판",
        "public": True,
    }


@pytest.fixture
def sample_post_data() -> Dict[str, Any]:
    """테스트용 샘플 게시글 데이터."""
    return {
        "title": "샘플 게시글",
        "content": "샘플 게시글 내용",
    }


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """테스트용 샘플 사용자 데이터."""
    return {
        "fullname": "Sample User",
        "email": "sample@example.com",
        "password": "samplepassword123",
    }


# 깨끗한 상태 보장을 위한 정리 픽스처
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """테스트 중 생성된 테스트 파일 정리."""
    yield
    # 필요한 경우 정리 로직 추가
    pass