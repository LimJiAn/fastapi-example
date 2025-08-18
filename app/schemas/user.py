from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    fullname: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    created: datetime
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
