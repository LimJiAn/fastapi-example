from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.crud.board import CRUDBoard
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardSortOption
from app.schemas.auth import CurrentUser


class BoardService:
    """게시판 관련 서비스"""

    def __init__(self, board_crud: CRUDBoard):
        self.board_crud = board_crud

    async def create(self, request: BoardCreate, current_user: CurrentUser, db: Session) -> BoardResponse:
        """게시판 생성

        Args:
            request: 게시판 생성 요청 데이터
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            BoardResponse: 생성된 게시판 정보

        Raises:
            HTTPException: 게시판 이름 중복 시 400
        """
        # 게시판 이름 중복 확인
        board = self.board_crud.get_by_name(db, name=request.name)
        if board:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 게시판 이름입니다"
            )

        try:
            new_board = self.board_crud.create_with_user(
                db, obj_in=request, owner_id=current_user.id
            )
            db.commit()
            
            return BoardResponse(
                id=new_board.id,
                name=new_board.name,
                public=new_board.public,
                owner_id=new_board.owner_id,
                created_at=new_board.created_at,
                updated_at=new_board.updated_at,
                post_count=0
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="게시판 생성에 실패했습니다"
            )

    def list(self, current_user: CurrentUser, db: Session, sort: BoardSortOption = BoardSortOption.created_at):
        """접근 가능한 게시판들의 SQLAlchemy Query 반환 (Cursor Pagination용)

        Args:
            current_user: 현재 사용자
            db: 데이터베이스 세션
            sort: 정렬 옵션

        Returns:
            SQLAlchemy Query: paginate 함수에서 사용할 쿼리
        """
        # 본인이 생성한 게시판 + 공개 게시판 쿼리
        # Cursor pagination을 위해 정렬 기준과 ID 함께 정렬 (안정적인 정렬 보장)
        return self.board_crud.get_accessible_boards(db, current_user.id, sort)

    async def get(self, board_id: int, current_user: CurrentUser, db: Session) -> BoardResponse:
        """게시판 조회

        Args:
            board_id: 게시판 ID
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            BoardResponse: 게시판 정보

        Raises:
            HTTPException: 권한 없음 시 403, 존재하지 않음 시 404
        """
        board = self.board_crud.get(db, id=board_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시판을 찾을 수 없습니다"
            )
        if not board.public and board.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시판에 접근할 권한이 없습니다"
            )
        # 게시글 수 계산
        post_count = self.board_crud.get_post_count(db, board_id=board_id)
        return BoardResponse(
            id=board.id,
            name=board.name,
            public=board.public,
            owner_id=board.owner_id,
            created_at=board.created_at,
            updated_at=board.updated_at,
            post_count=post_count
        )

    async def update(self, board_id: int, request: BoardUpdate, current_user: CurrentUser, db: Session) -> BoardResponse:
        """게시판 수정

        Args:
            board_id: 게시판 ID
            request: 게시판 수정 요청 데이터
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            BoardResponse: 수정된 게시판 정보

        Raises:
            HTTPException: 권한 없음 시 403, 존재하지 않음 시 404
        """
        board = self.board_crud.get(db, id=board_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시판을 찾을 수 없습니다"
            )
        if board.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시판을 수정할 권한이 없습니다"
            )
        # 이름 변경 시 중복 확인
        if request.name and request.name != board.name:
            existing_board = self.board_crud.get_by_name(db, name=request.name)
            if existing_board:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 게시판 이름입니다"
                )
        try:
            updated_board = self.board_crud.update(db, db_obj=board, obj_in=request)
            db.commit()
            
            # 게시글 수 계산
            post_count = self.board_crud.get_post_count(db, board_id=board_id)
            
            return BoardResponse(
                id=updated_board.id,
                name=updated_board.name,
                public=updated_board.public,
                owner_id=updated_board.owner_id,
                created_at=updated_board.created_at,
                updated_at=updated_board.updated_at,
                post_count=post_count
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="게시판 수정에 실패했습니다"
            )

    async def delete(self, board_id: int, current_user: CurrentUser, db: Session) -> None:
        """게시판 삭제

        Args:
            board_id: 게시판 ID
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            dict: 삭제 완료 메시지

        Raises:
            HTTPException: 권한 없음 시 403, 존재하지 않음 시 404
        """
        board = self.board_crud.get(db, id=board_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시판을 찾을 수 없습니다"
            )
        
        # 권한 확인: 게시판 생성자만 삭제 가능
        if board.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시판을 삭제할 권한이 없습니다"
            )

        try:
            self.board_crud.delete(db, id=board_id)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="게시판 삭제에 실패했습니다"
            )
