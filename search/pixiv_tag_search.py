from bs4 import BeautifulSoup
from db.db_session_manager import DBSessionManager
from exceptions.missing_data_exception import MissingDataException
from repositories.services.search_tag_service import SearchTagService
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import List


class PixivTagSearch(NovelSearchInterface):

    def fetch_novel_list(self) -> List[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []

        # タグ一覧を取得
        with DBSessionManager.session() as session:
            search_tag_service = SearchTagService(session)
            search_tag_model_list = search_tag_service.get_all()

        # Playwrightを使用してHTMLを取得
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            for tag in search_tag_model_list:
                # 各タグに対応するURLを生成
                base_url = EnvConfigLoader.get_variable("PIXIV_TAG_SEARCH_URL")
                url = base_url.format(tag=tag)  # {tags} プレースホルダーを置換

                # ページにアクセス
                try:
                    page.goto(url)
                    page.wait_for_load_state("domcontentloaded")  # DOM読み込み完了を待機
                    html = page.content()
                except Exception as e:
                    raise MissingDataException(
                        f"URL '{url}' のアクセス中にエラーが発生しました: {e}"
                    )

                # BeautifulSoupでHTMLをパース
                soup = BeautifulSoup(html, "html.parser")
                print(html)
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
                    if not novel_url:
                        raise MissingDataException(
                            f"タグ '{tag}' の小説にURLが取得できませんでした。"
                        )

                    # 小説情報を追加
                    # all_novels.append(
                    #     NovelSummary(title=title, source_url=novel_url, site=Site.NOCTURNE)
                    # )

            browser.close()

        return all_novels
