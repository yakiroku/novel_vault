
from datetime import datetime
from pydantic import BaseModel


class NovelMetadata(BaseModel):
    """小説のメタデータ（タイトル、著者、説明）を保持するクラス"""
    
    title: str
    """小説のタイトル"""
    author: str
    """小説の著者"""
    description: str
    """小説の説明"""
    tags: list[str]
    """小説のタグ"""
    last_posted_at: datetime
    """最終投稿日時"""
