from datetime import datetime
from typing import TYPE_CHECKING

from models import Base
from settings import LOCAL_TZ
from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.chapter_model import ChapterModel
    from models.novel_tag_model import NovelTagModel


class NovelModel(Base):
    """
    小説を管理するモデル
    """

    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    site: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    last_posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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
    excluded: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )  # 除外フラグを追加
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    # リレーション
    chapters: Mapped[list["ChapterModel"]] = relationship("ChapterModel", back_populates="novel")
    novel_tags: Mapped[list["NovelTagModel"]] = relationship(
        "NovelTagModel", back_populates="novel"
    )

    # 制約の名前を付ける
    __table_args__ = (
        # ユニーク制約の名前を指定
        UniqueConstraint("source_url", name="uq_novels_source_url"),
        # インデックスに名前を指定
        Index("ix_novels_source_url", "source_url"),
        Index("ix_novels_excluded", "excluded"),
    )
