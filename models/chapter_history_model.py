from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.chapter_model import ChapterModel


class ChapterHistoryModel(Base):
    """
    小説の章の履歴を管理するモデル
    """

    __tablename__ = "chapter_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id"""
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey("chapters.id"), nullable=False)
    """小説の章のid"""
    title: Mapped[str] = mapped_column(Text, nullable=False)
    """小説の章のタイトル"""
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    """小説の章の内容"""
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """小説の章の投稿日時"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )
    """作成日時"""

    # リレーション
    chapter: Mapped["ChapterModel"] = relationship("ChapterModel", back_populates="histories")
    """小説の章のリレーション"""

    # 制約の名前を付ける
    __table_args__ = (
        # インデックスに名前を指定
        Index("ix_chapter_histories_chapter_id", "chapter_id"),
        Index("ix_chapter_histories_posted_at", "posted_at"),
    )
