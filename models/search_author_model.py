from datetime import datetime
from models import Base
from settings import LOCAL_TZ
from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class SearchAuthorModel(Base):
    """
    検索対象の作者名を管理するモデル
    """

    __tablename__ = "search_authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 作者名
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )

    # ユニーク制約に名前を付ける
    __table_args__ = (
        UniqueConstraint('name', name='uq_search_authors_name'),  # nameカラムにユニーク制約を追加
    )