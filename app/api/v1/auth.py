from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.services.auth_service import AuthService
from app.api.v1.deps import get_current_user

router = APIRouter()

@router.post("/signup")
async def signup(user_data: Dict[str, Any] = None):
    """회원가입"""
    if user_data is None:
        user_data = {"email": "test@example.com", "fullname": "Test User"}
    
    result = await AuthService.signup(user_data)
    return result

@router.post("/login") 
async def login(credentials: Dict[str, Any] = None):
    """로그인"""
    if credentials is None:
        credentials = {"email": "test@example.com", "password": "testpassword"}
    
    result = await AuthService.login(credentials)
    return result

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """로그아웃"""
    result = await AuthService.logout("temp_user_id")
    return result
