import re
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


class KakuyomuTagSearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []

        sorteds = ["published_at", "weekly_ranking", "popular", "last_episode_published_at"]
        for sort in sorteds:
            # 各タグに対応するURLを生成
            url = f"{EnvConfigLoader.get_variable('KAKUYOMU_TAG_SEARCH_URL')}&order={sort}"
            all_novels.extend(self.fetch_kakuyomu_novels(url))
        return all_novels

        
    def fetch_kakuyomu_novels(self, url: str) -> list[NovelSummary]:
        """
        指定されたURLのページから小説のタイトルとURLを取得します。

        Args:
            url (str): 小説一覧ページのURL

        Returns:
            List[NovelSummary]: 小説のタイトルとURLのリスト

        Raises:
            MissingDataException: 必須データが取得できない場合
        """
        novel_summary_list = []

        # ページにリクエストを送信
        response = requests.get(url)
        response.raise_for_status()

        # HTML解析
        soup = BeautifulSoup(response.text, "html.parser")
        novels = soup.select("h3.Heading_heading__lQ85n a.LinkAppearance_link__POVTP")

        for novel in novels:
            # タイトルを取得
            title = novel.get_text(strip=True)
            if not title:
                raise MissingDataException("タグの小説にタイトルが取得できませんでした。")

            # URLを取得
            novel_url = novel.get("href")
            if not novel_url:
                raise MissingDataException("タグの小説にURLが取得できませんでした。")

            # KakuyomuのURLは相対パスなので、絶対URLに変換
            full_url = f"https://kakuyomu.jp{novel_url}"

            if re.match(r"^https://kakuyomu\.jp/works/\d+$", full_url):
                # 小説情報を追加
                novel_summary_list.append(NovelSummary(title=title, source_url=full_url, site=Site.KAKUYOMU))

        return novel_summary_list
