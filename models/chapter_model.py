from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.novel_model import NovelModel
    from models.chapter_history_model import ChapterHistoryModel


class ChapterModel(Base):
    """
    小説の章を管理するモデル
    """

    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("novels.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    source_url: Mapped[str] = mapped_column(String(255), nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(LOCAL_TZ),
        onupdate=lambda: datetime.now(LOCAL_TZ),
        nullable=False,
    )
    """更新日時"""

    # リレーション
    novel: Mapped["NovelModel"] = relationship("NovelModel", back_populates="chapters")
    histories: Mapped[list["ChapterHistoryModel"]] = relationship(
        "ChapterHistoryModel", back_populates="chapter"
    )

    # 制約の名前を付ける
    __table_args__ = (
        # UniqueConstraintの名前指定
        UniqueConstraint("source_url", name="uq_chapters_source_url"),
        # インデックスの名前指定
        Index("ix_chapters_novel_id", "novel_id"),
        Index("ix_chapters_posted_at", "posted_at"),
    )
