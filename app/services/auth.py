from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.auth import SignUpRequest, LoginRequest, SignUpResponse, LoginResponse, CurrentUser, LogoutResponse, UserInfo
from app.schemas.user import UserCreate
from app.core.security import create_access_token
from app.redis.session import create_session, delete_session


class AuthService:
    """인증 관련 서비스"""
    
    def __init__(self, user_crud: CRUDUser):
        self.user_crud = user_crud

    async def signup(self, request: SignUpRequest, db: Session) -> SignUpResponse:
        """회원가입 처리

        Args:
            request: 회원가입 요청 데이터
            db: 데이터베이스 세션

        Returns:
            SignUpResponse: 회원가입 응답

        Raises:
            HTTPException: 이메일 중복 시 409 에러
        """
        try:
            user = self.user_crud.get_by_email(db, email=request.email)
            if user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 존재하는 이메일입니다"
                )
            new_user = self.user_crud.create(
                db, obj_in=UserCreate(
                    fullname=request.fullname,
                    email=request.email,
                    password=request.password
                )
            )
            db.commit()
            return SignUpResponse(
                id=new_user.id,
                email=new_user.email,
                fullname=new_user.fullname,
                created_at=new_user.created_at
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="회원가입 중 오류가 발생했습니다"
            )
        except Exception:
            db.rollback()
            raise

    async def login(self, request: LoginRequest, db: Session) -> LoginResponse:
        """로그인 처리

        Args:
            request: 로그인 자격 증명
            db: 데이터베이스 세션

        Returns:
            LoginResponse: 로그인 응답 (액세스 토큰 포함)

        Raises:
            HTTPException: 인증 실패 시 401 에러
        """
        user = self.user_crud.authenticate(db, email=request.email, password=request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다"
            )
        access_token = create_access_token(data={"user_id": str(user.id)})
        try:
            # Redis에 세션 저장
            user_info = {
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            create_session(user.id, access_token, user_info)
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
                created_at=user.created_at
            )
        )

    @staticmethod
    async def logout(current_user: CurrentUser) -> LogoutResponse:
        """로그아웃 처리

        Args:
            current_user: 현재 로그인된 사용자

        Returns:
            LogoutResponse: 로그아웃 응답
        """
        delete_session(current_user.id)
        return LogoutResponse(
            message="로그아웃 되었습니다"
        )

    def get_user_by_id(self, user_id: int, db: Session) -> Optional[User]:
        """사용자 ID로 조회 (의존성 주입에서 사용)

        Args:
            user_id: 사용자 ID
            db: 데이터베이스 세션

        Returns:
            User: 사용자 객체 또는 None
        """
        return self.user_crud.get(db, id=user_id)
