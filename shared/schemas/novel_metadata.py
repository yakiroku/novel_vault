
from datetime import datetime
from pydantic import BaseModel


class NovelMetadata(BaseModel):
    """小説のメタデータ（タイトル、著者、説明）を保持するクラス"""
    
    title: str
    author: str
    description: str
    last_posted_at: datetime