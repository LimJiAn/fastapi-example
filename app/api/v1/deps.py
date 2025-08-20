from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.user import user as user_crud
from app.crud.board import board as board_crud
from app.crud.post import post as post_crud
from app.services.auth import AuthService
from app.services.board import BoardService
from app.services.post import PostService
from app.models.user import User
from app.redis.session import get_session, validate_session
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationError
)


# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """AuthService 의존성 주입"""
    return AuthService(user_crud=user_crud)


def get_board_service() -> BoardService:
    """BoardService 의존성 주입"""
    return BoardService(board_crud=board_crud)


def get_post_service() -> PostService:
    """PostService 의존성 주입"""
    return PostService(post_crud=post_crud, board_crud=board_crud)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """현재 로그인된 사용자 조회"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise AuthenticationError("사용자 ID가 없습니다")
    except Exception:
        raise AuthenticationError("토큰이 유효하지 않습니다")

    session_data = get_session(int(user_id))
    if not session_data:
        raise AuthenticationError("세션이 만료되었습니다")

    if not validate_session(int(user_id), credentials.credentials):
        raise AuthenticationError("세션이 유효하지 않습니다")

    user = auth_service.get_user_by_id(user_id=int(user_id), db=db)
    if user is None:
        raise AuthenticationError("사용자를 찾을 수 없습니다")

    return user