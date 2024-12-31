from bs4 import BeautifulSoup
import requests
from exceptions.missing_data_exception import MissingDataException
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader
from util.nocturne_helper import NocturneHelper


class NocturneRankedSearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """ランキングページから小説の一覧を取得する"""
        # ランキングのURLリストを環境変数から取得
        ranked_urls = [
            EnvConfigLoader.get_variable("NOCTURNE_DAILY_RANKED_URL"),
            EnvConfigLoader.get_variable("NOCTURNE_WEEKLY_RANKED_URL"),
            EnvConfigLoader.get_variable("NOCTURNE_MONTHLY_RANKED_URL"),
            EnvConfigLoader.get_variable("NOCTURNE_QUARTERLY_RANKED_URL"),
            EnvConfigLoader.get_variable("NOCTURNE_YEARLY_RANKED_URL"),
        ]

        novel_summaries = []

        # 各URLについて処理を繰り返す
        for url in ranked_urls:
            response = NocturneHelper.request(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            # <a class="tl"> タグを探す
            novels = soup.select("a.tl")  # class="tl" のaタグを全て取得

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
