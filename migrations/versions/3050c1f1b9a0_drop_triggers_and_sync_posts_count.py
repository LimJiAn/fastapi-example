"""drop_triggers_and_sync_posts_count

Revision ID: 3050c1f1b9a0
Revises: 2059bf0e827e
Create Date: 2025-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3050c1f1b9a0'
down_revision: Union[str, Sequence[str], None] = '2059bf0e827e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop DB triggers/functions and sync current counts to real post counts."""

    # Drop trigger and function if present (idempotent)
    op.execute("DROP TRIGGER IF EXISTS trigger_update_board_posts_count ON posts;")
    op.execute("DROP FUNCTION IF EXISTS update_board_posts_count();")

    # Synchronize existing posts_count with real data to ensure correctness
    op.execute("""
        UPDATE boards
        SET posts_count = (
            SELECT COUNT(*) FROM posts WHERE posts.board_id = boards.id
        )
    """)


def downgrade() -> None:
    """No-op for downgrade: restoring previous trigger is left to the
    original migration file if a downgrade path is needed.
    """
    pass
