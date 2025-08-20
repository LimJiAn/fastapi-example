"""테스트 유틸리티 및 헬퍼 함수."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.security import create_access_token


def create_test_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """주어진 사용자 ID로 테스트 JWT 토큰 생성."""
    if expires_delta:
        return create_access_token(
            data={"sub": str(user_id)}, 
            expires_delta_minutes=int(expires_delta.total_seconds() / 60)
        )
    return create_access_token(data={"sub": str(user_id)})


def create_auth_headers(user_id: int) -> Dict[str, str]:
    """주어진 사용자 ID로 인증 헤더 생성."""
    token = create_test_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def assert_board_response(response_data: Dict[str, Any], expected_data: Optional[Dict[str, Any]] = None) -> None:
    """게시판 응답 데이터가 예상 데이터와 일치하는지 검증."""
    if expected_data:
        assert response_data["name"] == expected_data["name"]
        if "public" in expected_data:
            assert response_data["public"] == expected_data["public"]
    
    # 기본 구조 확인
    assert "id" in response_data
    assert "name" in response_data
    assert "public" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert "owner_id" in response_data
    # posts_count 필드가 있는지 확인 (Board 응답에서는 posts_count로 나옴)
    assert "posts_count" in response_data or "post_count" in response_data


def assert_post_response(response_data: Dict[str, Any], expected_data: Optional[Dict[str, Any]] = None) -> None:
    """게시글 응답 데이터가 예상 데이터와 일치하는지 검증."""
    if expected_data:
        assert response_data["title"] == expected_data["title"]
        assert response_data["content"] == expected_data["content"]
    
    # 기본 구조 확인
    assert "id" in response_data
    assert "title" in response_data
    assert "content" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert "board_id" in response_data
    assert "owner_id" in response_data


def assert_user_response(response_data: Dict[str, Any], expected_data: Dict[str, Any]) -> None:
    """사용자 응답 데이터가 예상 데이터와 일치하는지 검증."""
    assert response_data["fullname"] == expected_data["fullname"]
    assert response_data["email"] == expected_data["email"]
    assert "id" in response_data
    assert "created_at" in response_data
    # 비밀번호가 포함되지 않았는지 확인
    assert "password" not in response_data
    assert "hashed_password" not in response_data


def assert_pagination_response(response_data: dict):
    """페이지네이션 응답 구조 검증"""
    assert "items" in response_data
    assert "total" in response_data
    assert "next_page" in response_data
    assert "previous_page" in response_data
    
    assert isinstance(response_data["items"], list)
    assert isinstance(response_data["total"], int)
    # next_page와 previous_page는 None이거나 문자열
    if response_data["next_page"] is not None:
        assert isinstance(response_data["next_page"], str)
    if response_data["previous_page"] is not None:
        assert isinstance(response_data["previous_page"], str)


def assert_error_response(response_data: dict, status_code: int, message: str = None):
    """에러 응답 구조 검증"""
    assert "detail" in response_data
    
    if message:
        # detail이 문자열이거나 리스트일 수 있음
        if isinstance(response_data["detail"], str):
            assert message in response_data["detail"]
        elif isinstance(response_data["detail"], list):
            # Validation error의 경우
            detail_str = str(response_data["detail"])
            assert message in detail_str
        else:
            assert message in str(response_data["detail"])


def assert_error_response(response_data: Dict[str, Any], expected_status: int, expected_message: str = None) -> None:
    """에러 응답 구조 검증."""
    assert "detail" in response_data
    if expected_message:
        assert expected_message in response_data["detail"]


class MockData:
    """테스트용 모킹 데이터 생성기."""
    
    @staticmethod
    def user_data(fullname: str = "Test User", email: str = "test@example.com") -> Dict[str, Any]:
        """사용자 데이터 생성."""
        return {
            "fullname": fullname,
            "email": email,
            "password": "testpassword123",
        }
    
    @staticmethod
    def board_data(name: str = "테스트 게시판", public: bool = True) -> Dict[str, Any]:
        """게시판 데이터 생성."""
        return {
            "name": name,
            "public": public,
        }
    
    @staticmethod
    def post_data(title: str = "테스트 게시글", content: str = "테스트 내용") -> Dict[str, Any]:
        """게시글 데이터 생성."""
        return {
            "title": title,
            "content": content,
        }
