import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.services.auth_service import AuthService
from app.schemas.auth import SignUpRequest, LoginRequest
from app.models.user import User
from datetime import datetime


class TestAuthService:
    """AuthService 단위 테스트"""

    @pytest.fixture
    def auth_service(self, mock_user_crud):
        """AuthService 인스턴스 생성"""
        return AuthService(user_crud=mock_user_crud)

    @pytest.fixture
    def sample_user(self):
        """테스트용 사용자 객체"""
        return User(
            id=1,
            fullname="테스트 유저",
            email="test@example.com",
            password="$2b$12$hashed_password",
            created=datetime.now()
        )

    @pytest.fixture
    def signup_request(self):
        """회원가입 요청 데이터"""
        return SignUpRequest(
            fullname="테스트 유저",
            email="test@example.com",
            password="testpassword123"
        )

    @pytest.fixture
    def login_request(self):
        """로그인 요청 데이터"""
        return LoginRequest(
            email="test@example.com",
            password="testpassword123"
        )

    @pytest.mark.asyncio
    async def test_signup_success(self, auth_service, mock_user_crud, signup_request, sample_user, db_session):
        """회원가입 성공 테스트"""
        # Given
        mock_user_crud.get_by_email.return_value = None  # 이메일 중복 없음
        mock_user_crud.create_with_password.return_value = sample_user
        
        # When
        with patch('app.services.auth_service.get_password_hash') as mock_hash:
            mock_hash.return_value = "$2b$12$hashed_password"
            result = await auth_service.signup(signup_request, db_session)

        # Then
        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.fullname == "테스트 유저"
        
        # Mock 호출 확인
        mock_user_crud.get_by_email.assert_called_once_with(db_session, email="test@example.com")
        mock_user_crud.create_with_password.assert_called_once()
        db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_email_already_exists(self, auth_service, mock_user_crud, signup_request, sample_user, db_session):
        """회원가입 실패 - 이메일 중복"""
        # Given
        mock_user_crud.get_by_email.return_value = sample_user  # 이미 존재하는 이메일
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.signup(signup_request, db_session)
        
        assert exc_info.value.status_code == 409
        assert "이미 존재하는 이메일입니다" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_signup_database_error(self, auth_service, mock_user_crud, signup_request, db_session):
        """회원가입 실패 - 데이터베이스 에러"""
        # Given
        mock_user_crud.get_by_email.return_value = None
        mock_user_crud.create_with_password.side_effect = IntegrityError("DB Error", None, None)
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            with patch('app.services.auth_service.get_password_hash'):
                await auth_service.signup(signup_request, db_session)
        
        assert exc_info.value.status_code == 409
        assert "회원가입 중 오류가 발생했습니다" in exc_info.value.detail
        db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_crud, login_request, sample_user, db_session):
        """로그인 성공 테스트"""
        # Given
        mock_user_crud.authenticate.return_value = sample_user
        mock_user_crud.is_active.return_value = True
        
        # When
        with patch('app.services.auth_service.create_access_token') as mock_token, \
             patch('app.services.auth_service.create_session') as mock_session:
            mock_token.return_value = "test_access_token"
            result = await auth_service.login(login_request, db_session)

        # Then
        assert result.access_token == "test_access_token"
        assert result.user.id == 1
        assert result.user.email == "test@example.com"
        
        # Mock 호출 확인
        mock_user_crud.authenticate.assert_called_once_with(
            db_session, email="test@example.com", password="testpassword123"
        )
        mock_user_crud.is_active.assert_called_once_with(sample_user)
        mock_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_service, mock_user_crud, login_request, db_session):
        """로그인 실패 - 잘못된 자격증명"""
        # Given
        mock_user_crud.authenticate.return_value = None  # 인증 실패
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(login_request, db_session)
        
        assert exc_info.value.status_code == 401
        assert "이메일 또는 비밀번호가 올바르지 않습니다" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, auth_service, mock_user_crud, login_request, sample_user, db_session):
        """로그인 실패 - 비활성화된 사용자"""
        # Given
        mock_user_crud.authenticate.return_value = sample_user
        mock_user_crud.is_active.return_value = False  # 비활성화됨
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(login_request, db_session)
        
        assert exc_info.value.status_code == 400
        assert "비활성화된 사용자입니다" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service):
        """로그아웃 성공 테스트"""
        # Given
        from app.schemas.auth import CurrentUser
        current_user = CurrentUser(id=1, email="test@example.com", fullname="테스트 유저")
        
        # When
        with patch('app.services.auth_service.delete_session') as mock_delete:
            result = await auth_service.logout(current_user)

        # Then
        assert result.message == "로그아웃 되었습니다"
        mock_delete.assert_called_once_with(1)

    def test_get_user_by_id_success(self, auth_service, mock_user_crud, sample_user, db_session):
        """사용자 ID 조회 성공 테스트"""
        # Given
        mock_user_crud.get.return_value = sample_user
        
        # When
        result = auth_service.get_user_by_id(1, db_session)
        
        # Then
        assert result == sample_user
        mock_user_crud.get.assert_called_once_with(db_session, id=1)

    def test_get_user_by_id_not_found(self, auth_service, mock_user_crud, db_session):
        """사용자 ID 조회 실패 테스트"""
        # Given
        mock_user_crud.get.return_value = None
        
        # When
        result = auth_service.get_user_by_id(999, db_session)
        
        # Then
        assert result is None
