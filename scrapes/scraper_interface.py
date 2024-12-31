from abc import ABC, abstractmethod

from shared.schemas.chapter import Chapter
from shared.schemas.chapter_content import ChapterContent
from shared.schemas.novel_metadata import NovelMetadata


class NovelScraperInterface(ABC):
    """小説サイトのスクレイピングに必要なインターフェース"""

    @abstractmethod
    def fetch_novel_metadata(self) -> NovelMetadata:
        """
        小説の基本情報（タイトル、著者、概要など）を取得する

        Args:
            novel_id (int): 対象小説のID

        Returns:
            Dict[str, str]: 小説の基本情報（例: {"title": "タイトル", "author": "著者名", "description": "概要"}）
        """
        pass

    @abstractmethod
    def fetch_chapter_list(self) -> list[Chapter]:
        """
        小説の章リストを取得する

        Args:
            novel_id (int): 対象小説のID

        Returns:
            List[Dict[str, str]]: 章リスト（例: [{"title": "章タイトル", "url": "章URL"}]）
        """
        pass

    @abstractmethod
    def fetch_chapter_content(self, chapter_url: str) -> ChapterContent:
        """
        章の内容を取得する

        Args:
            chapter_url (str): 章のURL

        Returns:
            str: 章の内容
        """
        pass
