from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from fastapi_pagination.cursor import CursorParams
from fastapi_pagination.ext.sqlalchemy import paginate


from app.db.session import get_db
from app.services.board import BoardService
from app.api.v1.deps import get_board_service, get_current_user
from app.schemas.board import (
    BoardCreate,
    BoardUpdate,
    BoardResponse,
    BoardListResponse,
    BoardSortOption
)
from app.schemas.auth import CurrentUser


router = APIRouter()

@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create(
    board_data: BoardCreate,
    current_user: CurrentUser = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
    db: Session = Depends(get_db)
):
    """
    게시판 생성
    
    - **name**: 게시판 이름 (unique 제약조건)
    - **public**: 공개 여부 (true: 전체 공개, false: 생성자만 접근)
    
    권한: 로그인한 사용자만 생성 가능

    Returns:
        BoardResponse: 생성된 게시판 정보

    Raises:
        HTTPException 409: 게시판 이름 중복
    """
    return await board_service.create(board_data, current_user, db)

@router.get("/", response_model=BoardListResponse)
async def list(
    params: CursorParams = Depends(),
    sort: BoardSortOption = Query(
        BoardSortOption.created_at,
        description="정렬 옵션 (created: 생성일순, posts: 게시글수순)"
    ),
    current_user: CurrentUser = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
    db: Session = Depends(get_db)
):
    """
    게시판 목록 조회 (Cursor Pagination 사용)
    
    Query Parameters:
    - **cursor**: 커서 토큰 (다음/이전 페이지용)
    - **size**: 페이지당 항목 수 (기본값: 20)
    - **sort**: 정렬 옵션
      - created: 생성일 순 (최신순, 기본값)
      - posts: 게시글 수 순 (많은순)
    
    권한: 로그인한 사용자, 본인이 생성한 게시판 + 공개 게시판만 조회 가능

    Returns:
        BoardListResponse: 게시판 목록 정보
    """
    # SQLAlchemy Query를 가져와서 paginate 함수에 전달
    query = board_service.list(current_user, db, sort)
    return paginate(db, query, params)

@router.get("/{board_id}", response_model=BoardResponse)
async def get(
    board_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
    db: Session = Depends(get_db)
):
    """
    게시판 상세 조회
    
    - **board_id**: 조회할 게시판 ID

    권한: 로그인한 사용자, 본인이 생성한 게시판 + 공개 게시판만 조회 가능

    Returns:
        BoardResponse: 게시판 정보

    Raises:
        HTTPException 404: 게시판 없음
        HTTPException 403: 접근 권한 없음
    """
    return await board_service.get(board_id, current_user, db)

@router.put("/{board_id}", response_model=BoardResponse)
async def update(
    board_id: int,
    board_update: BoardUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
    db: Session = Depends(get_db)
):
    """
    게시판 수정
    
    - **board_id**: 수정할 게시판 ID
    - **name**: 새로운 게시판 이름 (선택사항)
    - **public**: 새로운 공개 여부 (선택사항)
    
    권한: 게시판 생성자만 수정 가능

    Returns:
        BoardResponse: 수정된 게시판 정보

    Raises:
        HTTPException 404: 게시판 없음
        HTTPException 403: 접근 권한 없음
        HTTPException 409: 게시판 이름 중복
    """
    return await board_service.update(board_id, board_update, current_user, db)

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    board_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    board_service: BoardService = Depends(get_board_service),
    db: Session = Depends(get_db)
):
    """
    게시판 삭제
    
    - **board_id**: 삭제할 게시판 ID
    
    권한: 게시판 생성자만 삭제 가능

    Returns:
        BoardResponse: 삭제된 게시판 정보

    Raises:
        HTTPException 404: 게시판 없음
        HTTPException 403: 접근 권한 없음
    """
    return await board_service.delete(board_id, current_user, db)