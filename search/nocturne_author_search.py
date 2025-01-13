from bs4 import BeautifulSoup
from requests import Response
from db.db_session_manager import DBSessionManager
from exceptions.missing_data_exception import MissingDataException
from models.search_author_model import SearchAuthorModel
from repositories.services.search_author_service import SearchAuthorService
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader
from util.nocturne_helper import NocturneHelper
from util.scraping_helper import ScrapingHelper


class NocturneAuthorSearch(NovelSearchInterface):
    def fetch_novel_list(self) -> list[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []

        for author in self.get_all_search_authors():
            # 各タグに対応するURLを生成
            base_url = f"{EnvConfigLoader.get_variable('NOCTURNE_TAG_SEARCH_URL')}{author.name}&wname=1"
            all_novels.extend(self.fetch_novels_from_url(base_url))
        return all_novels

    def get_all_search_authors(self) -> list[SearchAuthorModel]:
        with DBSessionManager.session() as session:
            search_author_service = SearchAuthorService(session)
            return search_author_service.get_all()

    def fetch_novels_from_url(self, base_url: str) -> list[NovelSummary]:
        """指定したURLからすべてのページの小説情報を取得"""
        novel_summary_list = []
        current_page = 1

        while True:
            # 現在のページのURLを構築
            paged_url = f"{base_url}&p={current_page}"
            response: Response = NocturneHelper.request(paged_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            novels = soup.select("a.tl")  # class="tl" のaタグを全て取得

            if not novels:
                # 小説が見つからない場合はループを終了
                break

            for novel in novels:
                # タイトルを取得
                title = novel.get_text(strip=True)
                if not title:
                    raise MissingDataException("小説のタイトルが取得できませんでした。")

                # URLを取得
                novel_url = ScrapingHelper.get_first_value(novel.get("href"))
                if not novel_url:
                    raise MissingDataException("小説のURLが取得できませんでした。")

                # 小説情報をリストに追加
                novel_summary_list.append(
                    NovelSummary(title=title, source_url=novel_url, site=Site.NOCTURNE)
                )

            # 次のページがあるか確認
            next_page = soup.select_one("a.nextlink")
            if not next_page:
                # 次のページリンクが無い場合、全ページを処理済みとみなす
                break

            current_page += 1

        return novel_summary_list