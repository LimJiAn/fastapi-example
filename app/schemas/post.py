from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

from app.schemas.pagination import CursorPageCustom


class PostSortOption(str, Enum):
    """게시글 목록 정렬 옵션"""
    created_at = "created_at"    # 생성일 순 (최신순, 기본값)
    # title = "title"              # 제목 순


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    """게시글 생성 요청 스키마 (board_id는 URL에서)"""
    pass


class PostUpdate(BaseModel):
    """게시글 업데이트 요청 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None


class PostResponse(PostBase):
    """게시글 응답 스키마"""
    id: int
    owner_id: int
    board_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


PostListResponse = CursorPageCustom[PostResponse]