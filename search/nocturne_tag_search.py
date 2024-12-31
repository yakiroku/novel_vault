from bs4 import BeautifulSoup
import requests
from exceptions.missing_data_exception import MissingDataException
from search.novel_search_interface import NovelSearchInterface
from shared.enums.site import Site
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader


class NocturneTagSearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []

        for tag in EnvConfigLoader.get_variable("NOCTURNE_TAGS").split(","):
            # 各タグに対応するURLを生成
            url = f"{EnvConfigLoader.get_variable('NOCTURNE_TAG_SEARCH_URL')}{tag.strip()}"

            # クッキーとヘッダーの設定
            cookies = {
                "over18": "yes",  # 必要なクッキーを追加
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

            # クッキーをrequestsのgetに渡す
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
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
