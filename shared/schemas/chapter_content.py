from pydantic import BaseModel


class ChapterContent(BaseModel):
    """章の本文を保持するクラス"""
    
    content: str
    """章の本文"""