import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crud.post import CRUDPost
from app.crud.board import CRUDBoard
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostSortOption
from app.schemas.auth import CurrentUser
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, InternalServerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostService:
    """게시글 관련 서비스"""

    def __init__(self, post_crud: CRUDPost, board_crud: CRUDBoard):
        self.post_crud = post_crud
        self.board_crud = board_crud

    async def create(self, board_id: int, request: PostCreate, current_user: CurrentUser, db: Session) -> PostResponse:
        """게시글 생성

        Args:
            board_id: 게시판 ID
            request: 게시글 생성 요청 데이터
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            PostResponse: 생성된 게시글 정보

        Raises:
            HTTPException: 게시판 없을 시 404, 게시판 접근 권한 없음 시 403
        """
        board = self.board_crud.get(db, id=board_id)
        if not board:
            raise NotFoundError("존재하지 않는 게시판입니다")
        if not self.board_crud.check_board_access(db, current_user.id, board_id):
            raise ForbiddenError("해당 게시판에 게시글을 작성할 권한이 없습니다")
        try:
            db_post = self.post_crud.create_with_user(
                db, obj_in=request, owner_id=current_user.id, board_id=board_id
            )
            db.commit()
            return PostResponse(
                id=db_post.id,
                title=db_post.title,
                content=db_post.content,
                owner_id=db_post.owner_id,
                board_id=db_post.board_id,
                created_at=db_post.created_at,
                updated_at=db_post.updated_at
            )

        except IntegrityError:
            db.rollback()
            raise ConflictError("게시글 생성에 실패했습니다")

    def list(self, board_id: int, current_user: CurrentUser, db: Session, sort: PostSortOption = PostSortOption.created_at):
        """게시판의 게시글들의 SQLAlchemy Query 반환 (Cursor Pagination용)

        Args:
            board_id: 게시판 ID
            current_user: 현재 사용자
            db: 데이터베이스 세션
            sort: 정렬 옵션

        Returns:
            SQLAlchemy Query: paginate 함수에서 사용할 쿼리
        """
        # 게시판이 존재하고 접근 가능한지 확인
        board = self.board_crud.get(db, id=board_id)
        if not board:
            raise NotFoundError("존재하지 않는 게시판입니다")

        # 비공개 게시판이면서 소유자가 아닌 경우 접근 거부
        if not board.public and board.owner_id != current_user.id:
            raise ForbiddenError("해당 게시판에 접근할 권한이 없습니다")
            
        return self.post_crud.get_accessible_posts(db, current_user.id, board_id, sort)

    async def get(self, post_id: int, current_user: CurrentUser, db: Session) -> PostResponse:
        """게시글 조회

        Args:
            post_id: 게시글 ID
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            PostResponse: 게시글 정보

        Raises:
            HTTPException: 권한 없음 시 403
        """
        post = self.post_crud.get_accessible_post(db, current_user.id, post_id)
        if not post:
            raise ForbiddenError("게시글을 찾을 수 없거나 접근 권한이 없습니다")

        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            owner_id=post.owner_id,
            board_id=post.board_id,
            created_at=post.created_at,
            updated_at=post.updated_at
        )

    async def update(self, post_id: int, request: PostUpdate, current_user: CurrentUser, db: Session) -> PostResponse:
        """게시글 수정

        Args:
            post_id: 게시글 ID
            request: 게시글 수정 요청 데이터
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Returns:
            PostResponse: 수정된 게시글 정보

        Raises:
            HTTPException: 권한 없음 시 403, 존재하지 않음 시 404
        """
        post = self.post_crud.get(db, id=post_id)
        if not post:
            raise NotFoundError("게시글을 찾을 수 없습니다")
        if post.owner_id != current_user.id:
            raise ForbiddenError("게시글을 수정할 권한이 없습니다")
        try:
            updated_post = self.post_crud.update(db, db_obj=post, obj_in=request)
            db.commit()
            
            return PostResponse(
                id=updated_post.id,
                title=updated_post.title,
                content=updated_post.content,
                owner_id=updated_post.owner_id,
                board_id=updated_post.board_id,
                created_at=updated_post.created_at,
                updated_at=updated_post.updated_at
            )

        except IntegrityError:
            db.rollback()
            raise ConflictError("게시글 수정에 실패했습니다")

    async def delete(self, post_id: int, current_user: CurrentUser, db: Session) -> None:
        """게시글 삭제

        Args:
            post_id: 게시글 ID
            current_user: 현재 사용자
            db: 데이터베이스 세션

        Raises:
            HTTPException: 권한 없음 시 403, 존재하지 않음 시 404
        """
        post = self.post_crud.get(db, id=post_id)
        if not post:
            raise NotFoundError("게시글을 찾을 수 없습니다")
        if post.owner_id != current_user.id:
            raise ForbiddenError("게시글을 삭제할 권한이 없습니다")

        try:
            self.post_crud.delete(db, id=post_id)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"게시글 삭제 중 오류 발생: {e}")
            raise InternalServerError("게시글 삭제에 실패했습니다")
