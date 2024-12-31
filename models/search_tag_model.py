from datetime import datetime
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class SearchTagModel(Base):
    """
    検索対象タグを管理するモデル
    """

    __tablename__ = "search_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )

    # ユニーク制約に名前を付ける
    __table_args__ = (
        UniqueConstraint('name', name='uq_search_tags_name'),  # nameカラムにユニーク制約を追加
    )