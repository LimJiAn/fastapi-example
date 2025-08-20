from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate, BoardSortOption


class CRUDBoard(CRUDBase[Board, BoardCreate, BoardUpdate]):

    def get_by_name(self, db: Session, *, name: str) -> Optional[Board]:
        """게시판 이름으로 조회"""
        return db.query(Board).filter(Board.name == name).first()

    def create_with_user(self, db: Session, *, obj_in: BoardCreate, owner_id: int) -> Board:
        """사용자 ID와 함께 게시판 생성"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id
        )
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def get_accessible_boards(
        self, db: Session, user_id: int, sort: BoardSortOption = BoardSortOption.created_at):
        """사용자가 접근 가능한 게시판들의 Query 반환 (Cursor Pagination용)
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            sort: 정렬 옵션
            
        Returns:
            SQLAlchemy Query: 본인 생성 + 공개 게시판 (정렬 적용)
        """
        query = db.query(Board).filter(
            and_(
                # 본인이 생성하거나 공개된 게시판
                (Board.owner_id == user_id) | (Board.public == True)
            )
        )
        # 정렬 옵션에 따른 처리
        if sort == BoardSortOption.posts:
            # 게시글 수로 정렬 (많은순) - 트리거로 관리되는 posts_count 컬럼 사용
            query = query.order_by(Board.posts_count.desc(), Board.id.desc())
        # elif sort == BoardSortOption.name:
        #     # 이름순 정렬
        #     query = query.order_by(Board.name.asc(), Board.id.desc())
        # elif sort == BoardSortOption.updated:
        #     # 수정일순 정렬
        #     query = query.order_by(
        #         func.coalesce(Board.updated_at, Board.created_at).desc(),
        #         Board.id.desc()
        #     )
        else:  # sort == BoardSortOption.created_at (기본값)
            # 생성일순 정렬 (최신순)
            query = query.order_by(Board.created_at.desc(), Board.id.desc())
        
        return query

    def check_board_access(self, db: Session, user_id: int, board_id: int) -> bool:
        """게시판 접근 권한 확인"""
        board = db.query(Board).filter(Board.id == board_id).first()
        if not board:
            return False
        if not board:
            return False
        return board.public or board.owner_id == user_id

board = CRUDBoard(Board)
