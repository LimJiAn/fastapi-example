from pydantic import BaseModel, EmailStr
from datetime import datetime

class SignUpRequest(BaseModel):
    """회원가입 요청 스키마"""
    fullname: str
    email: EmailStr
    password: str

class SignUpResponse(BaseModel):
    """회원가입 응답 스키마"""
    id: int
    email: str
    fullname: str
    created_at: datetime

class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    access_token: str
    token_type: str = "Bearer"
    user: 'UserInfo'

class UserInfo(BaseModel):
    """사용자 정보 스키마"""
    id: int
    email: str
    fullname: str
    created_at: datetime

class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str

class CurrentUser(BaseModel):
    """현재 사용자 스키마 (인증에서 사용)"""
    id: int
    email: str
    fullname: str

# Forward reference 해결
LoginResponse.model_rebuild()