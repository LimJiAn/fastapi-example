from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from fastapi_pagination.ext.sqlalchemy import paginate

from app.db.session import get_db
from app.services.post import PostService
from app.api.v1.deps import get_post_service, get_current_user
from app.schemas.post import (
    PostCreate,
    PostUpdate, 
    PostResponse,
    PostListResponse,
    PostSortOption
)
from app.schemas.pagination import TotalCursorParams
from app.schemas.auth import CurrentUser


router = APIRouter()

@router.post("/boards/{board_id}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create(
    board_id: int = Path(..., description="게시판 ID"),
    post_data: PostCreate = ...,
    current_user: CurrentUser = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
    db: Session = Depends(get_db)
):
    """
    게시글 생성
    
    - **board_id**: 게시판 ID (URL 경로)
    - **title**: 게시글 제목
    - **content**: 게시글 내용
    
    권한: 로그인한 사용자 + 접근 가능한 게시판에만 생성 가능

    Returns:
        PostResponse: 생성된 게시글 정보

    Raises:
        HTTPException 404: 게시판 없음
        HTTPException 403: 접근 권한 없음
    """
    return await post_service.create(board_id, post_data, current_user, db)

@router.get("/boards/{board_id}/posts", response_model=PostListResponse)
def list(
    board_id: int = Path(..., description="게시판 ID"),
    params: TotalCursorParams = Depends(),
    sort: PostSortOption = Query(
        PostSortOption.created_at, 
        description="정렬 옵션 (created_at: 생성일순)"
    ),
    current_user: CurrentUser = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
    db: Session = Depends(get_db)
):
    """
    특정 게시판의 게시글 목록 조회 (Cursor Pagination)
    
    Query Parameters:
    - **cursor**: 커서 토큰 (다음/이전 페이지용)
    - **size**: 페이지당 항목 수 (기본값: 50)
    - **sort**: 정렬 옵션
      - created_at: 생성일 순 (최신순, 기본값)
      - name: 이름 순

    권한: 로그인한 사용자 + 접근 가능한 게시판의 게시글만 조회 가능

    Returns:
        PostListResponse: 게시글 목록 정보

    Raises:
        HTTPException 404: 게시판 없음
        HTTPException 403: 접근 권한 없음
    """
    stmt = post_service.list(board_id, current_user, db, sort)
    return paginate(db, stmt, params)

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get(
    post_id: int = Path(..., description="게시글 ID"),
    current_user: CurrentUser = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
    db: Session = Depends(get_db)
):
    """
    게시글 상세 조회
    
    - **post_id**: 조회할 게시글 ID

    권한: 로그인한 사용자 + 접근 가능한 게시판의 게시글만 조회 가능

    Returns:
        PostResponse: 게시글 정보

    Raises:
        HTTPException 404: 게시글 없음
        HTTPException 403: 접근 권한 없음
    """
    return await post_service.get(post_id, current_user, db)

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update(
    post_id: int = Path(..., description="게시글 ID"),
    post_update: PostUpdate = ...,
    current_user: CurrentUser = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
    db: Session = Depends(get_db)
):
    """
    게시글 수정
    
    - **post_id**: 수정할 게시글 ID
    - **title**: 새로운 제목 (선택사항)
    - **content**: 새로운 내용 (선택사항)
    
    권한: 게시글 작성자만 수정 가능

    Returns:
        PostResponse: 수정된 게시글 정보

    Raises:
        HTTPException 403: 권한 없음
        HTTPException 404: 게시글 없음
    """
    return await post_service.update(post_id, post_update, current_user, db)

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    post_id: int = Path(..., description="게시글 ID"),
    current_user: CurrentUser = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
    db: Session = Depends(get_db)
):
    """
    게시글 삭제
    
    - **post_id**: 삭제할 게시글 ID
    
    권한: 게시글 작성자만 삭제 가능
    """
    return await post_service.delete(post_id, current_user, db)