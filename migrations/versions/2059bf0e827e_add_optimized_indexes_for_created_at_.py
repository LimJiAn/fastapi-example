"""add_optimized_indexes_for_created_at_desc_sorting

Revision ID: 2059bf0e827e
Revises: 2d5177af924c
Create Date: 2025-08-20 06:59:07.880312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2059bf0e827e'
down_revision: Union[str, Sequence[str], None] = '2d5177af924c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # public + created_at DESC 복합 인덱스
    op.create_index(
        'ix_boards_public_created_at_desc', 
        'boards', 
        ['public', sa.text('created_at DESC')], 
        unique=False
    )
    
    # board_id + created_at DESC 정렬을 위한 복합 인덱스
    op.create_index(
        'ix_posts_board_id_created_at_desc',
        'posts',
        ['board_id', sa.text('created_at DESC')],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 인덱스 제거 (생성 역순으로)
    op.drop_index('ix_posts_board_id_created_at_desc', table_name='posts')
    op.drop_index('ix_boards_public_created_at_desc', table_name='boards')
