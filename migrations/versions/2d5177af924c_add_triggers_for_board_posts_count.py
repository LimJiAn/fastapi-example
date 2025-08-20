"""Add triggers for board posts_count

Revision ID: 2d5177af924c
Revises: 2fc7d77492f6
Create Date: 2025-08-20 03:38:32.263543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d5177af924c'
down_revision: Union[str, Sequence[str], None] = '2fc7d77492f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add triggers for automatic posts_count management."""

    # 0. 기존 트리거 및 함수 삭제
    op.execute("DROP TRIGGER IF EXISTS trigger_update_board_posts_count ON posts;")
    op.execute("DROP FUNCTION IF EXISTS update_board_posts_count();")

    # 1. 기존 데이터의 posts_count 초기화 (실제 게시글 수로 동기화)
    op.execute("""
        UPDATE boards 
        SET posts_count = (
            SELECT COUNT(*) 
            FROM posts 
            WHERE posts.board_id = boards.id
        )
    """)

    # 2. 트리거 함수 생성
    op.execute("""
        CREATE OR REPLACE FUNCTION update_board_posts_count()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                -- 게시글 추가시 카운트 증가
                UPDATE boards 
                SET posts_count = posts_count + 1 
                WHERE id = NEW.board_id;
                RETURN NEW;

            ELSIF TG_OP = 'DELETE' THEN
                -- 게시글 삭제시 카운트 감소 (음수 방지)
                UPDATE boards 
                SET posts_count = GREATEST(posts_count - 1, 0)
                WHERE id = OLD.board_id;
                RETURN OLD;

            ELSIF TG_OP = 'UPDATE' THEN
                -- 게시글 UPDATE는 title, content만 변경되므로 posts_count에 영향 없음
                RETURN NEW;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 3. 트리거 생성 (posts 테이블의 INSERT/UPDATE/DELETE 시 실행)
    op.execute("""
        CREATE TRIGGER trigger_update_board_posts_count
            AFTER INSERT OR UPDATE OR DELETE ON posts
            FOR EACH ROW
            EXECUTE FUNCTION update_board_posts_count();
    """)

def downgrade() -> None:
    """Remove triggers for posts_count management."""

    # 트리거 삭제
    op.execute("DROP TRIGGER IF EXISTS trigger_update_board_posts_count ON posts;")

    # 트리거 함수 삭제  
    op.execute("DROP FUNCTION IF EXISTS update_board_posts_count();")
