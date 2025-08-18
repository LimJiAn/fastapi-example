from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token
from app.core.redis_session import session
from app.schemas.auth import CurrentUser

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """현재 로그인된 사용자 조회 (JWT 토큰 + Redis 세션 기반)
    
    Args:
        credentials: HTTP Bearer 토큰

    Returns:
        CurrentUser: 현재 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시 401 에러
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 토큰입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # JWT 토큰에서 사용자 ID 추출
        print("credentials.credentials:", credentials.credentials)
        user_id_str = verify_token(credentials.credentials)
        
        if user_id_str is None:
            raise credentials_exception
        
        user_id = int(user_id_str)

        # Redis 세션 검증
        is_valid_session = await session.validate_session(user_id, credentials.credentials)
        print(is_valid_session)
        if not is_valid_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="세션이 만료되었거나 유효하지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (ValueError, TypeError):
        raise credentials_exception
    
    # 세션에서 사용자 정보 조회
    session_data = await session.get_session(user_id)
    if session_data and session_data.get("user_info"):
        user_info = session_data["user_info"]
        current_user = CurrentUser(
            id=user_info.get("id"),
            email=user_info.get("email"),
            fullname=user_info.get("fullname"),
            created=user_info.get("created")
        )
    else:
        #TODO: 세션이 없는 경우
        pass
    return current_user