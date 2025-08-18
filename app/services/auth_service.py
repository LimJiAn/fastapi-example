from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.schemas.auth import SignUpRequest, LoginRequest, SignUpResponse, LoginResponse, CurrentUser, LogoutResponse, UserInfo
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.core.redis_session import session


class AuthService:
    """인증 관련 서비스"""
    
    @staticmethod
    async def signup(request: SignUpRequest, db: Session) -> SignUpResponse:
        """회원가입 처리

        Args:
            user_data: 회원가입 요청 데이터
            db: 데이터베이스 세션

        Returns:
            SignUpResponse: 회원가입 응답

        Raises:
            HTTPException: 이메일 중복 시 409 에러
        """
        # 이메일 중복 확인
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 이메일입니다"
            )

        # 새 사용자 생성
        hashed_password = get_password_hash(request.password)
        new_user = User(
            fullname=request.fullname,
            email=request.email,
            password=hashed_password
        )

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="회원가입 중 오류가 발생했습니다"
            )

        return SignUpResponse(
            id=new_user.id,
            email=new_user.email,
            fullname=new_user.fullname,
            created=new_user.created
        )

    @staticmethod
    async def login(request: LoginRequest, db: Session) -> LoginResponse:
        """로그인 처리

        Args:
            request: 로그인 자격 증명
            db: 데이터베이스 세션

        Returns:
            LoginResponse: 로그인 응답 (액세스 토큰 포함)

        Raises:
            HTTPException: 인증 실패 시 401 에러
        """
        # 사용자 조회
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다"
            )
        
        # 비밀번호 검증
        if not verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다"
            )
        # JWT 토큰 생성
        access_token = create_access_token(data={"user_id": str(user.id)})

        # Redis에 세션 저장
        try:
            user_info = {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname,
                "created": user.created.isoformat() if user.created else None
            }
            await session.create_session(user.id, access_token, user_info)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="로그인 중 오류가 발생했습니다"
            )

        return LoginResponse(
            access_token=access_token,
            user=UserInfo(
                id=user.id,
                email=user.email,
                fullname=user.fullname,
                created=user.created
            )
        )

    @staticmethod
    async def logout(current_user: CurrentUser) -> LogoutResponse:
        await session.delete_session(current_user.id)
        return LogoutResponse(
            message="로그아웃 되었습니다"
        )
