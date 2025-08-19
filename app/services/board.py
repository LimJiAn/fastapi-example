from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.crud.board import CRUDBoard
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardListResponse
from app.schemas.auth import CurrentUser


class BoardService:
    """게시판 관련 서비스"""
    
    def __init__(self, board_crud: CRUDBoard):
        self.board_crud = board_crud

    async def create_board(self, request: BoardCreate, current_user: CurrentUser, db: Session) -> BoardResponse:
        """게시판 생성 처리

        Args:
            request: 게시판 생성 요청 데이터
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            BoardResponse: 게시판 생성 응답

        Raises:
            HTTPException: 이름 중복 시 409 에러
        """
        try:
            # 이름 중복 확인
            existing_board = self.board_crud.get_by_name(db, name=request.name)
            if existing_board:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 존재하는 게시판 이름입니다"
                )
            
            # 게시판 생성
            new_board = self.board_crud.create_with_user(
                db, 
                obj_in=request, 
                created_by=current_user.id
            )
            
            db.commit()
            return BoardResponse(
                id=new_board.id,
                name=new_board.name,
                public=new_board.public,
                created_by=new_board.created_by,
                created=new_board.created,
                updated=new_board.updated,
                post_count=0
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="게시판 생성 중 오류가 발생했습니다"
            )
        except Exception:
            db.rollback()
            raise

    async def get_board(self, board_id: int, current_user: CurrentUser, db: Session) -> BoardResponse:
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
        
        # 권한 확인: 본인이 생성하거나 공개된 게시판만 조회 가능
        if not board.public and board.created_by != current_user.id:
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
            created_by=board.created_by,
            created=board.created,
            updated=board.updated,
            post_count=post_count
        )

    async def update_board(self, board_id: int, request: BoardUpdate, current_user: CurrentUser, db: Session) -> BoardResponse:
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
        
        # 권한 확인: 본인이 생성한 게시판만 수정 가능
        if board.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시판을 수정할 권한이 없습니다"
            )
        
        try:
            # 이름 중복 확인 (다른 게시판과 중복되는지)
            if request.name and request.name != board.name:
                existing_board = self.board_crud.get_by_name(db, name=request.name)
                if existing_board and existing_board.id != board_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="이미 존재하는 게시판 이름입니다"
                    )
            
            updated_board = self.board_crud.update(db, db_obj=board, obj_in=request)
            db.commit()
            
            # 게시글 수 계산
            post_count = self.board_crud.get_post_count(db, board_id=board_id)
            
            return BoardResponse(
                id=updated_board.id,
                name=updated_board.name,
                public=updated_board.public,
                created_by=updated_board.created_by,
                created=updated_board.created,
                updated=updated_board.updated,
                post_count=post_count
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="게시판 수정 중 오류가 발생했습니다"
            )
        except Exception:
            db.rollback()
            raise

    async def delete_board(self, board_id: int, current_user: CurrentUser, db: Session) -> dict:
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
        
        # 권한 확인: 본인이 생성한 게시판만 삭제 가능
        if board.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시판을 삭제할 권한이 없습니다"
            )
        
        try:
            self.board_crud.remove(db, id=board_id)
            db.commit()
            return {"message": "게시판이 삭제되었습니다"}
        except Exception:
            db.rollback()
            raise

    async def list_boards(self, current_user: CurrentUser, db: Session, sort_by_posts: bool = False) -> BoardListResponse:
        """게시판 목록 조회

        Args:
            current_user: 현재 사용자
            db: 데이터베이스 세션
            sort_by_posts: 게시글 수로 정렬 여부

        Returns:
            BoardListResponse: 게시판 목록

        Notes:
            본인이 생성하거나 공개된 게시판만 조회 가능
        """
        boards = self.board_crud.get_accessible_boards(
            db, 
            user_id=current_user.id,
            sort_by_posts=sort_by_posts
        )
        
        board_responses = []
        for board in boards:
            post_count = self.board_crud.get_post_count(db, board_id=board.id)
            board_responses.append(BoardResponse(
                id=board.id,
                name=board.name,
                public=board.public,
                created_by=board.created_by,
                created=board.created,
                updated=board.updated,
                post_count=post_count
            ))
        
        return BoardListResponse(
            boards=board_responses,
            total=len(board_responses)
        )