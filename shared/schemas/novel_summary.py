from pydantic import BaseModel

from shared.enums.site import Site


class NovelSummary(BaseModel):
    """小説のタイトルとURLを保持する汎用的なクラス"""

    title: str
    """小説のタイトル"""
    source_url: str
    """小説のURL"""
    site: Site
    """小説のサイト"""
