from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class Board(Base):
    __tablename__ = "boards"
    __table_args__ = (
        Index("ix_boards_posts_count_desc_id_desc", "posts_count", "id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    posts_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="boards")
    posts: Mapped[List["Post"]] = relationship(
        back_populates="board", cascade="all, delete-orphan", passive_deletes=True
    )