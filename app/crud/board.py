from typing import Optional
from sqlalchemy.orm import Session
import sqlalchemy as sa
from sqlalchemy import func, or_, select

from app.crud.base import CRUDBase
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate, BoardSortOption
from sqlalchemy import update


class CRUDBoard(CRUDBase[Board, BoardCreate, BoardUpdate]):

    def get_by_name(self, db: Session, *, name: str) -> Optional[Board]:
        """게시판 이름으로 조회"""
        stmt = select(Board).where(Board.name == name)
        result = db.execute(stmt)
        return result.scalars().first()

    def create_with_user(self, db: Session, *, obj_in: BoardCreate, owner_id: int) -> Board:
        """사용자 ID와 함께 게시판 생성"""
        obj_in_data = obj_in.model_dump()
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
        """사용자가 접근 가능한 게시판들의 Select 반환
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            sort: 정렬 옵션
            
        Returns:
            SQLAlchemy Select: 본인 생성 + 공개 게시판 (정렬 적용)
        """
        # 본인이 생성한 게시판 OR 공개 게시판 
        stmt = select(Board).where(
            or_(Board.owner_id == user_id, Board.public == True)
        )
        
        # 정렬 옵션에 따른 처리
        if sort == BoardSortOption.posts:
            # 게시글 수로 정렬 (많은순) - 트리거로 관리되는 posts_count 컬럼 사용
            stmt = stmt.order_by(Board.posts_count.desc(), Board.id.desc())
        elif sort == BoardSortOption.name:
            # 이름순 정렬
            stmt = stmt.order_by(Board.name.asc(), Board.id.desc())
        elif sort == BoardSortOption.updated_at:
            # 수정일순 정렬
            stmt = stmt.order_by(
                func.coalesce(Board.updated_at, Board.created_at).desc(),
                Board.id.desc()
            )
        else:
            # 생성일순 정렬 (최신순)
            stmt = stmt.order_by(Board.created_at.desc(), Board.id.desc())
        
        return stmt

    def check_board_access(self, db: Session, user_id: int, board_id: int) -> bool:
        """게시판 접근 권한 확인"""
        stmt = select(Board).where(Board.id == board_id)
        result = db.execute(stmt)
        board = result.scalars().first()
        if not board:
            return False
        return board.public or board.owner_id == user_id

    def change_posts_count(self, db: Session, board_id: int, delta: int = 1) -> None:
        """boards.posts_count 증가/감소 (delta 양수면 증가, 음수면 감소). 음수로 내려가지 않음."""
        new_value = sa.case(
            [(Board.posts_count + delta < 0, 0)],
            else_=Board.posts_count + delta
        )
        stmt = update(Board).where(Board.id == board_id).values(
            posts_count=new_value
        )
        db.execute(stmt)

board = CRUDBoard(Board)
