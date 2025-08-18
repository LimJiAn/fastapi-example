import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app


class TestAuthAPI:
    """Auth API 통합 테스트"""

    @pytest.fixture
    def client(self):
        """FastAPI 테스트 클라이언트"""
        return TestClient(app)

    def test_signup_success(self, client):
        """회원가입 API 성공 테스트"""
        # Given
        signup_data = {
            "fullname": "테스트 유저",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # AuthService.signup을 Mock으로 대체
        with patch('app.api.v1.endpoints.auth.get_auth_service') as mock_get_service:
            mock_auth_service = Mock()
            mock_get_service.return_value = mock_auth_service
            
            from app.schemas.auth import SignUpResponse
            from datetime import datetime
            
            mock_auth_service.signup.return_value = SignUpResponse(
                id=1,
                email="test@example.com",
                fullname="테스트 유저",
                created=datetime.now()
            )
            
            # When
            response = client.post("/api/v1/auth/signup", json=signup_data)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["fullname"] == "테스트 유저"
        assert data["id"] == 1

    def test_signup_invalid_email(self, client):
        """회원가입 API 실패 - 잘못된 이메일"""
        # Given
        signup_data = {
            "fullname": "테스트 유저",
            "email": "invalid-email",  # 잘못된 이메일 형식
            "password": "testpassword123"
        }
        
        # When
        response = client.post("/api/v1/auth/signup", json=signup_data)

        # Then
        assert response.status_code == 422  # 유효성 검사 실패

    def test_login_success(self, client):
        """로그인 API 성공 테스트"""
        # Given
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # AuthService.login을 Mock으로 대체
        with patch('app.api.v1.endpoints.auth.get_auth_service') as mock_get_service:
            mock_auth_service = Mock()
            mock_get_service.return_value = mock_auth_service
            
            from app.schemas.auth import LoginResponse, UserInfo
            from datetime import datetime
            
            mock_auth_service.login.return_value = LoginResponse(
                access_token="test_access_token",
                user=UserInfo(
                    id=1,
                    email="test@example.com",
                    fullname="테스트 유저",
                    created=datetime.now()
                )
            )
            
            # When
            response = client.post("/api/v1/auth/login", json=login_data)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["user"]["email"] == "test@example.com"

    def test_logout_success(self, client):
        """로그아웃 API 성공 테스트"""
        # Given
        headers = {"Authorization": "Bearer test_access_token"}
        
        # 의존성들을 Mock으로 대체
        with patch('app.api.v1.deps.get_current_user') as mock_get_user, \
             patch('app.api.v1.endpoints.auth.AuthService.logout') as mock_logout:
            
            from app.models.user import User
            from app.schemas.auth import LogoutResponse
            from datetime import datetime
            
            # Mock 사용자
            mock_user = User(
                id=1,
                email="test@example.com",
                fullname="테스트 유저",
                password="hashed",
                created=datetime.now()
            )
            mock_get_user.return_value = mock_user
            mock_logout.return_value = LogoutResponse(message="로그아웃 되었습니다")
            
            # When
            response = client.post("/api/v1/auth/logout", headers=headers)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "로그아웃 되었습니다"

    def test_logout_unauthorized(self, client):
        """로그아웃 API 실패 - 인증되지 않음"""
        # Given (헤더 없음)
        
        # When
        response = client.post("/api/v1/auth/logout")

        # Then
        assert response.status_code == 403  # Forbidden (Bearer 토큰 필요)

    def test_signup_duplicate_email(self, client):
        """회원가입 API 실패 - 중복 이메일"""
        # Given
        signup_data = {
            "fullname": "테스트 유저",
            "email": "existing@example.com",
            "password": "testpassword123"
        }
        
        # AuthService에서 HTTPException 발생하도록 Mock
        with patch('app.api.v1.endpoints.auth.get_auth_service') as mock_get_service:
            mock_auth_service = Mock()
            mock_get_service.return_value = mock_auth_service
            
            from fastapi import HTTPException
            mock_auth_service.signup.side_effect = HTTPException(
                status_code=409,
                detail="이미 존재하는 이메일입니다"
            )
            
            # When
            response = client.post("/api/v1/auth/signup", json=signup_data)

        # Then
        assert response.status_code == 409
        data = response.json()
        assert "이미 존재하는 이메일입니다" in data["detail"]
