from pydantic import BaseModel

from shared.enums.site import Site


class NovelSummary(BaseModel):
    """小説のタイトルとURLを保持する汎用的なクラス"""

    title: str
    source_url: str
    site: Site
