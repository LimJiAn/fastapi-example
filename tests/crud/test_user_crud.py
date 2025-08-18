import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.db.base_class import Base
from app.models.user import User
from app.crud.user import user as user_crud
from app.schemas.auth import SignUpRequest


# 테스트용 SQLite DB
TEST_DATABASE_URL = "sqlite:///./test_crud.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestUserCRUD:
    """User CRUD 테스트"""
    
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """테스트용 데이터베이스 설정"""
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        yield
        # 테이블 삭제
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture
    def db_session(self):
        """테스트용 DB 세션"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_user_data(self):
        """테스트용 사용자 데이터"""
        return SignUpRequest(
            fullname="테스트 유저",
            email="test@example.com",
            password="testpassword123"
        )

    def test_create_user(self, db_session, sample_user_data):
        """사용자 생성 테스트"""
        # Given
        hashed_password = "$2b$12$test_hashed_password"
        
        # When
        created_user = user_crud.create_with_password(
            db_session, 
            user_in=sample_user_data, 
            hashed_password=hashed_password
        )
        db_session.commit()  # 테스트에서는 수동으로 commit

        # Then
        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.fullname == "테스트 유저"
        assert created_user.password == hashed_password
        assert created_user.created is not None

    def test_get_by_email(self, db_session, sample_user_data):
        """이메일로 사용자 조회 테스트"""
        # Given - 먼저 사용자 생성
        hashed_password = "$2b$12$test_hashed_password"
        created_user = user_crud.create_with_password(
            db_session, 
            user_in=sample_user_data, 
            hashed_password=hashed_password
        )
        db_session.commit()
        
        # When
        found_user = user_crud.get_by_email(db_session, email="test@example.com")
        
        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_by_email_not_found(self, db_session):
        """이메일로 사용자 조회 실패 테스트"""
        # When
        found_user = user_crud.get_by_email(db_session, email="nonexistent@example.com")
        
        # Then
        assert found_user is None

    def test_authenticate_success(self, db_session, sample_user_data):
        """인증 성공 테스트"""
        # Given - 사용자 생성
        hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "secret" 해시
        created_user = user_crud.create_with_password(
            db_session,
            user_in=sample_user_data,
            hashed_password=hashed_password
        )
        db_session.commit()
        
        # When
        with pytest.mock.patch('app.crud.crud_user.verify_password') as mock_verify:
            mock_verify.return_value = True
            authenticated_user = user_crud.authenticate(
                db_session, 
                email="test@example.com", 
                password="secret"
            )
        
        # Then
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

    def test_authenticate_wrong_password(self, db_session, sample_user_data):
        """인증 실패 - 잘못된 비밀번호"""
        # Given - 사용자 생성
        hashed_password = "$2b$12$test_hashed_password"
        user_crud.create_with_password(
            db_session,
            user_in=sample_user_data,
            hashed_password=hashed_password
        )
        db_session.commit()
        
        # When
        with pytest.mock.patch('app.crud.crud_user.verify_password') as mock_verify:
            mock_verify.return_value = False
            authenticated_user = user_crud.authenticate(
                db_session,
                email="test@example.com",
                password="wrong_password"
            )
        
        # Then
        assert authenticated_user is None

    def test_authenticate_user_not_found(self, db_session):
        """인증 실패 - 사용자 없음"""
        # When
        authenticated_user = user_crud.authenticate(
            db_session,
            email="nonexistent@example.com",
            password="anypassword"
        )
        
        # Then
        assert authenticated_user is None

    def test_is_active(self, db_session, sample_user_data):
        """사용자 활성화 상태 확인"""
        # Given
        hashed_password = "$2b$12$test_hashed_password"
        created_user = user_crud.create_with_password(
            db_session,
            user_in=sample_user_data,
            hashed_password=hashed_password
        )
        db_session.commit()
        
        # When
        is_active = user_crud.is_active(created_user)
        
        # Then
        assert is_active is True  # 현재는 항상 True

    def test_get_user_by_id(self, db_session, sample_user_data):
        """ID로 사용자 조회 테스트"""
        # Given
        hashed_password = "$2b$12$test_hashed_password"
        created_user = user_crud.create_with_password(
            db_session,
            user_in=sample_user_data,
            hashed_password=hashed_password
        )
        db_session.commit()
        
        # When
        found_user = user_crud.get(db_session, id=created_user.id)
        
        # Then
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"
