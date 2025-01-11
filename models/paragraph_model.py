from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Base
from settings import LOCAL_TZ
from tidb_vector.sqlalchemy import VectorType

if TYPE_CHECKING:
    from models.chapter_model import ChapterModel


class ParagraphModel(Base):
    """
    小説の章の段落ごとに分割したモデル
    """

    __tablename__ = "paragraphs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chapters.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # embedding: Mapped[list[float]] = mapped_column(VectorType(dim=768))  # ベクトルを格納するカラム
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )

    # リレーション
    chapter: Mapped["ChapterModel"] = relationship("ChapterModel", back_populates="paragraphs")

    __table_args__ = (
        # インデックスの名前指定
        Index("ix_paragraphs_chapter_id", "chapter_id"),
    )
