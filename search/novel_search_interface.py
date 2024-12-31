from abc import ABC, abstractmethod

from shared.schemas.novel_summary import NovelSummary


class NovelSearchInterface(ABC):
    """小説サイトのスクレイピングに必要なインターフェース"""


    @abstractmethod
    def fetch_novel_list(self) -> list[NovelSummary]:
        """
        小説の章リストを取得する

        Args:
            novel_id (int): 対象小説のID

        Returns:
            List[Dict[str, str]]: 章リスト（例: [{"title": "章タイトル", "url": "章URL"}]）
        """
        pass
