from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth import AuthService
from app.api.v1.deps import get_auth_service, get_current_user
from app.schemas.auth import (
    SignUpRequest, 
    LoginRequest, 
    SignUpResponse, 
    LoginResponse, 
    LogoutResponse
)
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=SignUpResponse)
async def signup(
    user_data: SignUpRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """회원가입

    계정 정보(fullname, email, password)를 입력받아 계정을 생성합니다.

    - **fullname**: 사용자 이름
    - **email**: 이메일 주소
    - **password**: 비밀번호

    Returns:
        SignUpResponse: 생성된 사용자 정보

    Raises:
        HTTPException 409: 이미 존재하는 이메일
        HTTPException 400: 유효하지 않은 입력 데이터
    """
    return await auth_service.signup(user_data, db)

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """로그인

    email, password를 입력받아 계정에 로그인하고, 해당 로그인 세션의 access token을 반환합니다.

    - **email**: 등록된 이메일 주소
    - **password**: 계정 비밀번호

    Returns:
        LoginResponse: 액세스 토큰과 사용자 정보

    Raises:
        HTTPException 401: 이메일 또는 비밀번호 오류
    """
    return await auth_service.login(credentials, db)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """로그아웃

    현재 로그인 세션을 로그아웃합니다.

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        LogoutResponse: 로그아웃 완료 메시지

    Raises:
        HTTPException 401: 유효하지 않은 토큰
    """
    # User 모델을 CurrentUser 스키마로 변환
    from app.schemas.auth import CurrentUser
    current_user_data = CurrentUser(
        id=current_user.id,
        email=current_user.email,
        fullname=current_user.fullname
    )
    return await AuthService.logout(current_user_data)