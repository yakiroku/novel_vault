from bs4 import BeautifulSoup
import requests
from exceptions.missing_data_exception import MissingDataException
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader


class NocturneRankedSearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """ランキングページから小説の一覧を取得する"""
        url = EnvConfigLoader.get_variable("NOCTURNE_RANKED_URL")

        # ブラウザから取得したクッキーをここに追加
        cookies = {
            "over18": "yes",  # 例: "session_id": "abcd1234"
            # 必要なクッキーをすべて追加
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        # クッキーをrequestsのgetに渡す
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # <a class="tl"> タグを探す
        novels = soup.select("a.tl")  # class="tl" のaタグを全て取得

        novel_summaries = []
        for novel in novels:
            title = novel.get_text(strip=True)
            novel_url = novel.get("href")

            if not title:
                raise MissingDataException("タイトルが取得できませんでした。")

            if isinstance(novel_url, list):
                if not novel_url:
                    raise MissingDataException("URLリストが空です。")
                novel_url = novel_url[0]  # 最初のURLを使用
            elif not novel_url:
                raise MissingDataException("URLが取得できませんでした。")

            novel_summaries.append(
                NovelSummary(title=title, source_url=novel_url, site=Site.NOCTURNE)
            )

        return novel_summaries
