from datetime import datetime
from pydantic import BaseModel


class Chapter(BaseModel):
    """目次の章情報（タイトル、URL）を保持するクラス"""

    title: str
    source_url: str
    posted_at: datetime
