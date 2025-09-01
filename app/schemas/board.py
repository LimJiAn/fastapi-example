from enum import Enum
from typing import Optional, Annotated
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pagination import CursorPageCustom

class BoardSortOption(str, Enum):
    """게시판 목록 정렬 옵션"""
    created_at = "created_at"  # 생성일 순 (최신순, 기본값)
    updated_at = "updated_at"  # 수정일 순
    posts = "posts"            # 게시글 수 순 (많은순)
    name = "name"              # 이름 순


class BoardBase(BaseModel):
    name: str
    public: bool


class BoardCreate(BoardBase):
    """게시판 생성 요청 스키마"""
    pass


class BoardUpdate(BaseModel):
    """게시판 업데이트 요청 스키마"""
    name: Optional[str] = None
    public: Optional[bool] = None


class BoardResponse(BoardBase):
    """게시판 응답 스키마"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    post_count: Annotated[int, Field(alias="posts_count")] = 0
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


BoardListResponse = CursorPageCustom[BoardResponse]
