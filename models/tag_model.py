from datetime import datetime
from typing import TYPE_CHECKING
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.novel_tag_model import NovelTagModel


class TagModel(Base):
    """
    タグを管理するモデル
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    # NovelTagModelとのリレーション
    novel_tags: Mapped[list["NovelTagModel"]] = relationship("NovelTagModel", back_populates="tag")