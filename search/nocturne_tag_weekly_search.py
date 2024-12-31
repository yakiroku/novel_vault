from bs4 import BeautifulSoup
import requests
from db.db_session_manager import DBSessionManager
from exceptions.missing_data_exception import MissingDataException
from models.search_tag_model import SearchTagModel
from repositories.services.search_tag_service import SearchTagService
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader
from util.nocturne_helper import NocturneHelper


class NocturneTagWeeklySearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []

        with DBSessionManager.session() as session:
            search_tag_service = SearchTagService(session)
            search_tag_model_list = search_tag_service.get_all()

        search_tag_model_list.append(SearchTagModel(name="", site=Site.NOCTURNE))
        
        for tag in search_tag_model_list:
            # 各タグに対応するURLを生成
            url = f"{EnvConfigLoader.get_variable('NOCTURNE_TAG_SEARCH_URL')}{tag.name}&order=weekly"
            # クッキーをrequestsのgetに渡す
            response = NocturneHelper.request(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            novels = soup.select("a.tl")  # class="tl" のaタグを全て取得

            for novel in novels:
                # タイトルを取得
                title = novel.get_text(strip=True)
                if not title:
                    raise MissingDataException(
                        f"タグ '{tag}' の小説にタイトルが取得できませんでした。"
                    )

                # URLを取得
                novel_url = novel.get("href")
                if isinstance(novel_url, list):
                    if not novel_url:
                        raise MissingDataException(f"タグ '{tag}' の小説にURLリストが空です。")
                    novel_url = novel_url[0]  # 最初のURLを使用
                elif not novel_url:
                    raise MissingDataException(f"タグ '{tag}' の小説にURLが取得できませんでした。")

                # 小説情報を追加
                all_novels.append(
                    NovelSummary(title=title, source_url=novel_url, site=Site.NOCTURNE)
                )

        return all_novels
