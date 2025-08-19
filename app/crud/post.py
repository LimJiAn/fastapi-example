from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.crud.base import CRUDBase
from app.models.post import Post
from app.models.board import Board
from app.schemas.post import PostCreate, PostUpdate, PostSortOption


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    
    def create_with_user(self, db: Session, *, obj_in: PostCreate, owner_id: int, board_id: int) -> Post:
        """사용자 ID와 게시판 ID로 게시글 생성"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            board_id=board_id
        )
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def get_accessible_posts(
        self, 
        db: Session, 
        user_id: int, 
        board_id: int,
        sort: PostSortOption = PostSortOption.created_at
    ):
        """사용자가 접근 가능한 게시글들의 Query 반환 (Cursor Pagination용)
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            board_id: 게시판 ID
            sort: 정렬 옵션
            
        Returns:
            SQLAlchemy Query: 접근 가능한 게시글 (정렬 적용)
        """
        # 게시판 접근 권한 확인을 포함한 쿼리
        query = db.query(Post).join(Board).filter(
            and_(
                Post.board_id == board_id,
                or_(
                    Board.owner_id == user_id,
                    Board.public == True
                )
            )
        )
        # 정렬 옵션에 따른 처리
        # if sort == PostSortOption.title:
        #     제목순 정렬
        #     query = query.order_by(Post.title.asc(), Post.id.desc())
        # else:
        #   생성일순 정렬 (최신순)
        query = query.order_by(Post.created_at.desc(), Post.id.desc())

        return query

    def get_accessible_post(self, db: Session, user_id: int, post_id: int) -> Optional[Post]:
        """사용자가 접근 가능한 게시글 조회"""
        return db.query(Post).join(Board).filter(
            and_(
                Post.id == post_id,
                or_(
                    Board.owner_id == user_id,
                    Board.public == True
                )
            )
        ).first()

# CRUD 인스턴스 생성
post = CRUDPost(Post)
