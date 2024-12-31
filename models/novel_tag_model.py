from datetime import datetime
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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