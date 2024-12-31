from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey("chapters.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )

    # リレーション
    chapter: Mapped["ChapterModel"] = relationship("ChapterModel", back_populates="histories")