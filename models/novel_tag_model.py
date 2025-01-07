from datetime import datetime
from typing import TYPE_CHECKING
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.novel_model import NovelModel
    from models.tag_model import TagModel


class NovelTagModel(Base):
    """
    小説とタグの中間テーブル
    """

    __tablename__ = "novel_tags"
    __table_args__ = (UniqueConstraint("novel_id", "tag_id"),)

    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("novels.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )

    # TagModelとのリレーション
    tag: Mapped["TagModel"] = relationship("TagModel", back_populates="novel_tags")

    # NovelModelとのリレーション
    novel: Mapped["NovelModel"] = relationship("NovelModel", back_populates="novel_tags")
