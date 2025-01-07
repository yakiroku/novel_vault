from datetime import datetime
from pydantic import BaseModel


class Chapter(BaseModel):
    """目次の章情報（タイトル、URL）を保持するクラス"""

    title: str
    """章タイトル"""
    source_url: str
    """章のURL"""
    posted_at: datetime
    """更新日時"""
