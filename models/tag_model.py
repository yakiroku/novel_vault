from datetime import datetime
from typing import TYPE_CHECKING
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import BigInteger, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.novel_model import NovelModel


class TagModel(Base):
    """
    タグを管理するモデル
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    # リレーション
    novels: Mapped[list["NovelModel"]] = relationship(
        "NovelModel", secondary="novel_tags", back_populates="tags"
    )
