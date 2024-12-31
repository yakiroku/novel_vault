from datetime import datetime
from typing import TYPE_CHECKING
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from models.novel_model import NovelModel


class ScrapeLogModel(Base):
    """
    スクレイピング履歴を管理するモデル
    """
    __tablename__ = "scrape_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, ForeignKey("novels.id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )  
    # リレーション
    novel: Mapped["NovelModel"] = relationship("NovelModel")