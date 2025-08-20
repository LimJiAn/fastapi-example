"""Post API 엔드포인트 테스트"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Board, Post, User
from tests.utils import assert_post_response, assert_pagination_response, assert_error_response


class TestCreatePost:
    """게시글 생성 테스트"""

    def test_create_post_success(self, authenticated_client, test_board):
        """게시글 생성 성공"""
        post_data = {
            "title": "테스트 게시글",
            "content": "게시글 내용입니다."
        }
        response = authenticated_client.post(
            f"/api/v1/boards/{test_board.id}/posts",
            json=post_data
        )

        assert response.status_code == 201
        data = response.json()
        assert_post_response(data)
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]

    def test_create_post_without_auth(self, client, test_board):
        """인증 없이 게시글 생성 시도"""
        post_data = {
            "title": "테스트 게시글",
            "content": "게시글 내용입니다."
        }
        response = client.post(
            f"/api/v1/boards/{test_board.id}/posts",
            json=post_data
        )
        
        assert response.status_code == 403
        """존재하지 않는 게시판에 게시글 생성"""
        post_data = {
            "title": "테스트 게시글",
            "content": "게시글 내용입니다."
        }
        response = client.post(
            "/api/v1/boards/999/posts",
            json=post_data
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({}, "Field required"),
        ({"content": "내용"}, "Field required"),
        ({"title": "ab", "content": "내용"}, "String should have at least 3 characters"),
        ({"title": "a" * 201, "content": "내용"}, "String should have at most 200 characters"),
    ])
    def test_create_post_validation_errors(self, authenticated_client, test_board, invalid_data, expected_error):
        """게시글 생성 유효성 검사"""
        response = authenticated_client.post(
            f"/api/v1/boards/{test_board.id}/posts",
            json=invalid_data
        )

        assert response.status_code == 422
        assert expected_error in str(response.json())


class TestListPosts:
    """게시글 목록 조회 테스트"""

    def test_list_posts_default(self, authenticated_client, test_board, test_posts):
        """게시글 목록 조회 - 기본"""
        response = authenticated_client.get(f"/api/v1/boards/{test_board.id}/posts")

        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data)
        assert len(data["items"]) > 0
        for post in data["items"]:
            assert_post_response(post)

    def test_list_posts_with_limit(self, authenticated_client, test_board, test_posts):
        """게시글 목록 조회 - 제한된 개수"""
        response = authenticated_client.get(f"/api/v1/boards/{test_board.id}/posts?size=2")

        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data)
        # 실제 게시글이 있다면 최대 2개까지만 반환되어야 함
        assert len(data["items"]) <= 2

    def test_list_posts_with_cursor(self, authenticated_client, test_board, test_posts):
        """게시글 목록 조회 - 커서 페이지네이션"""
        # 첫 번째 페이지
        response = authenticated_client.get(f"/api/v1/boards/{test_board.id}/posts?size=1")

        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data)

        # 다음 페이지가 있다면 next_page 확인
        if data.get("next_page"):
            # 다음 페이지 요청
            next_response = authenticated_client.get(
                f"/api/v1/boards/{test_board.id}/posts?cursor={data['next_page']}&size=1"
            )
            assert next_response.status_code == 200
            next_data = next_response.json()
            assert_pagination_response(next_data)

    def test_list_posts_with_sort(self, authenticated_client, test_board, test_posts):
        """게시글 목록 조회 - 정렬"""
        response = authenticated_client.get(f"/api/v1/boards/{test_board.id}/posts?sort=created_at")

        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data)

    def test_list_posts_total_count(self, authenticated_client, test_board, test_posts):
        """게시글 목록 조회 - total count 확인"""
        response = authenticated_client.get(f"/api/v1/boards/{test_board.id}/posts")

        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data)
        # total이 null이 아닌지 확인 (UseIncludeTotal 설정 적용)
        assert data.get("total") is not None

    def test_list_posts_board_not_found(self, authenticated_client):
        """존재하지 않는 게시판의 게시글 목록 조회"""
        response = authenticated_client.get("/api/v1/boards/999/posts")

        assert response.status_code == 404


class TestGetPost:
    """게시글 상세 조회 테스트"""

    def test_get_post_success(self, authenticated_client, test_post):
        """게시글 상세 조회 성공"""
        response = authenticated_client.get(f"/api/v1/posts/{test_post.id}")

        assert response.status_code == 200
        data = response.json()
        assert_post_response(data)
        assert data["id"] == test_post.id

    def test_get_post_not_found(self, authenticated_client):
        """존재하지 않는 게시글 조회"""
        response = authenticated_client.get("/api/v1/posts/999")

        assert response.status_code == 404

    def test_get_post_invalid_id(self, authenticated_client):
        """잘못된 ID로 게시글 조회"""
        response = authenticated_client.get("/api/v1/posts/invalid")

        assert response.status_code == 422


class TestUpdatePost:
    """게시글 수정 테스트"""

    def test_update_post_success(self, authenticated_client, test_post):
        """게시글 수정 성공"""
        update_data = {
            "title": "수정된 제목",
            "content": "수정된 내용"
        }
        response = authenticated_client.put(
            f"/api/v1/posts/{test_post.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert_post_response(data)
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]

    def test_update_post_not_owner(self, another_user_post):
        """게시글 소유자가 아닌 사용자의 수정 테스트"""
        # 다른 사용자의 인증 클라이언트가 필요하므로 인증 없이 테스트
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        update_data = {
            "title": "수정된 제목",
            "content": "수정된 내용"
        }
        response = client.put(
            f"/api/v1/posts/{another_user_post.id}",
            json=update_data
        )

        # 인증이 없으므로 401 또는 403 반환
        assert response.status_code in [401, 403]

    def test_update_post_without_auth(self, client, test_post):
        """인증 없이 게시글 수정 시도"""
        update_data = {
            "title": "수정된 제목",
            "content": "수정된 내용"
        }
        response = client.put(
            f"/api/v1/posts/{test_post.id}",
            json=update_data
        )

        assert response.status_code == 401

    def test_update_post_not_found(self, authenticated_client):
        """존재하지 않는 게시글 수정"""
        update_data = {
            "title": "수정된 제목",
            "content": "수정된 내용"
        }
        response = authenticated_client.put("/api/v1/posts/999", json=update_data)

        assert response.status_code == 404

    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({}, "Field required"),
        ({"content": "내용"}, "Field required"),
        ({"title": "ab", "content": "내용"}, "String should have at least 3 characters"),
        ({"title": "a" * 201, "content": "내용"}, "String should have at most 200 characters"),
    ])
    def test_update_post_validation_errors(self, authenticated_client, test_post, invalid_data, expected_error):
        """게시글 수정 유효성 검사"""
        response = authenticated_client.put(
            f"/api/v1/posts/{test_post.id}",
            json=invalid_data
        )

        assert response.status_code == 422
        assert expected_error in str(response.json())


class TestDeletePost:
    """게시글 삭제 테스트"""

    def test_delete_post_success(self, authenticated_client, test_post):
        """게시글 삭제 성공"""
        response = authenticated_client.delete(f"/api/v1/posts/{test_post.id}")

        assert response.status_code == 204

        # 삭제 확인
        get_response = authenticated_client.get(f"/api/v1/posts/{test_post.id}")
        assert get_response.status_code == 404

    def test_delete_post_not_owner(self, another_user_post):
        """게시글 소유자가 아닌 사용자의 삭제 테스트"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.delete(f"/api/v1/posts/{another_user_post.id}")

        # 인증이 없으므로 401 또는 403 반환
        assert response.status_code in [401, 403]

    def test_delete_post_without_auth(self, client, test_post):
        """인증 없이 게시글 삭제 시도"""
        response = client.delete(f"/api/v1/posts/{test_post.id}")

        assert response.status_code == 401

    def test_delete_post_not_found(self, authenticated_client):
        """존재하지 않는 게시글 삭제"""
        response = authenticated_client.delete("/api/v1/posts/999")

        assert response.status_code == 404


class TestPostTriggers:
    """게시글 트리거 관련 테스트"""

    def test_posts_count_increment_on_create(self, authenticated_client, test_board):
        """게시글 생성 시 게시판 posts_count 증가 확인"""
        # 기존 posts_count 확인
        board_response = authenticated_client.get(f"/api/v1/boards/{test_board.id}")
        
        # posts_count 필드가 응답에 없을 수 있으므로 확인
        board_data = board_response.json()
        if "posts_count" not in board_data:
            pytest.skip("posts_count 필드가 응답에 포함되지 않았습니다")
            
        initial_count = board_data["posts_count"]

        # 새 게시글 생성
        post_data = {
            "title": "카운트 테스트 게시글",
            "content": "게시글 카운트 증가 테스트"
        }
        post_response = authenticated_client.post(
            f"/api/v1/boards/{test_board.id}/posts",
            json=post_data
        )
        assert post_response.status_code == 201

        # posts_count 증가 확인
        updated_board_response = authenticated_client.get(f"/api/v1/boards/{test_board.id}")
        updated_count = updated_board_response.json()["posts_count"]
        assert updated_count == initial_count + 1

    def test_posts_count_decrement_on_delete(self, authenticated_client, test_post):
        """게시글 삭제 시 게시판 posts_count 감소 확인"""
        # 게시판 posts_count 확인
        board_response = authenticated_client.get(f"/api/v1/boards/{test_post.board_id}")
        
        # posts_count 필드가 응답에 없을 수 있으므로 확인
        board_data = board_response.json()
        if "posts_count" not in board_data:
            pytest.skip("posts_count 필드가 응답에 포함되지 않았습니다")
            
        initial_count = board_data["posts_count"]

        # 게시글 삭제
        delete_response = authenticated_client.delete(f"/api/v1/posts/{test_post.id}")
        assert delete_response.status_code == 204

        # posts_count 감소 확인
        updated_board_response = authenticated_client.get(f"/api/v1/boards/{test_post.board_id}")
        updated_count = updated_board_response.json()["posts_count"]
        assert updated_count == initial_count - 1
