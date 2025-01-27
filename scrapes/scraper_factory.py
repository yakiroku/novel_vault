from models.novel_model import NovelModel
from scrapes.kakuyomu_scraper import KakuyomuScraper
from scrapes.nocturne_scraper import NocturneScraper
from scrapes.scraper_interface import NovelScraperInterface
from shared.enums.site import Site


class ScraperFactory:
    """サイトに応じたスクレイパーを生成するファクトリクラス"""

    @staticmethod
    def create_scraper(novel: NovelModel) -> NovelScraperInterface:
        """
        スクレイパーを生成する

        Args:
            site_name (str): サイト名（例: "site_a", "site_b"）
            base_url (str): ベースURL

        Returns:
            NovelScraperInterface: 対応するスクレイパー
        """
        match novel.site:
            case Site.NOCTURNE.value:
                return NocturneScraper(novel)
            case Site.KAKUYOMU.value:
                return KakuyomuScraper(novel)
            case _:
                raise ValueError(f"Unsupported site: {novel.source_url}")
