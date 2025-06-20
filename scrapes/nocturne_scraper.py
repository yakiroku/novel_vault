from datetime import datetime
import re
from bs4 import BeautifulSoup, Tag
import requests
from exceptions.missing_data_exception import MissingDataException
from models.novel_model import NovelModel
from scrapes.scraper_interface import NovelScraperInterface
from settings import LOCAL_TZ
from shared.schemas.chapter import Chapter
from shared.schemas.chapter_content import ChapterContent
from shared.schemas.novel_metadata import NovelMetadata
from util.env_config_loader import EnvConfigLoader
from util.nocturne_helper import NocturneHelper
from util.scraping_helper import ScrapingHelper


class NocturneScraper(NovelScraperInterface):
    """Nocturneサイト専用のスクレイパークラス"""

    def __init__(self, novel: NovelModel):
        """
        初期化

        Args:
            base_url (str): NocturneサイトのベースURL
        """
        self.novel = novel

    def fetch_novel_metadata(self) -> NovelMetadata | None:
        """
        小説のメタデータ（タイトル、著者、説明）を取得する

        Args:
            novel_id (int): 小説のID

        Returns:
            NovelMetadata: 小説のメタデータ
        """
        response = NocturneHelper.request(self.novel.source_url)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        # タイトルを取得
        title_element = soup.select_one(".p-novel__title")
        title = title_element.text.strip() if title_element else "タイトルなし"

        # 作者名を取得
        author_element = soup.select_one(".p-novel__author")
        author = author_element.text.strip() if author_element else "作者不明"
        author = re.sub(r"\s+", "", author).replace("作者：", "")

        # 説明文を取得
        description_element = soup.select_one(".p-novel__summary")
        description = description_element.text.strip() if description_element else "説明なし"

        # タグを取得
        # meta タグの content 属性からタグを取得
        meta_tag = soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and isinstance(meta_tag, Tag) and "content" in meta_tag.attrs:
            tag_string = ScrapingHelper.get_first_value(meta_tag["content"])
            tag_string = tag_string.strip() if tag_string else ""
            # タグをスペースで区切ってリストを作成し、各タグに対して strip() を適用
            tags = [tag.strip() for tag in tag_string.split(" ")]
        else:
            tags = []  # タグが見つからない場合は空リスト

        # 最終更新日時を取得
        last_posted_at_element = soup.find("meta", {"name": "WWWC"})
        if isinstance(last_posted_at_element, Tag):
            last_posted_at = (
                last_posted_at_element["content"] if last_posted_at_element else "更新日時不明"
            )
        # last_posted_atがリストの場合、最初の要素を取り出す
        last_posted_at = ScrapingHelper.get_first_value(last_posted_at) or "更新日時不明"
        # datetime型に変換
        try:
            last_posted_at_datetime = datetime.strptime(last_posted_at, "%Y/%m/%d %H:%M")
            last_posted_at_datetime = LOCAL_TZ.localize(last_posted_at_datetime)
        except ValueError:
            last_posted_at_datetime = datetime(
                1970, 1, 1, 0, 0, 0, tzinfo=LOCAL_TZ
            )  # フォーマットが合わない場合はNoneにする

        novel_code = self.extract_identifier_from_url(self.novel.source_url)
        novel_view_url = f"{EnvConfigLoader.get_variable("NOCTURNE_NOVEL_VIEW_URL")}{novel_code}"
        response = NocturneHelper.request(novel_view_url)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        # ノベルタイプを取得
        completed = False
        novel_type = soup.select_one("#noveltype")
        novel_type = novel_type.text.strip() if novel_type else ""
        print(novel_type)
        if novel_type == "完結済" or novel_type == "短編":
            completed = True

        return NovelMetadata(
            title=title,
            author=author,
            description=description,
            tags=tags,
            last_posted_at=last_posted_at_datetime,
            completed=completed,
        )

    def fetch_chapter_list(self, novel_metadata: NovelMetadata) -> list[Chapter]:
        """
        小説の目次（章タイトルとURL）を取得する

        Args:
            novel_id (int): 小説のID

        Returns:
            List[Chapter]: Chapterオブジェクトのリスト
        """
        chapters = []  # 章情報を格納するリスト
        current_url = self.novel.source_url

        while current_url:
            response = NocturneHelper.request(current_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # 目次の取得
            chapter_elements = soup.select(".p-eplist__sublist")
            for chapter in chapter_elements:
                title_element = chapter.select_one(".p-eplist__subtitle")
                if title_element:
                    title = title_element.text.strip()
                    url = title_element.get("href")
                    url = ScrapingHelper.get_first_value(url)
                    if url is None:
                        raise MissingDataException("次のページURLが取得できませんでした。")

                    # 投稿日時を取得
                    update_element = chapter.select_one(".p-eplist__update")
                    if update_element:
                        # 投稿日時を取得（改稿日も含む）
                        posted_at_text = update_element.text.strip().split(" ")[
                            0
                        ]  # 最初の日付部分を取得

                        # 改稿がある場合、title属性から改稿日を取得
                        revised_date_element = update_element.select_one("span[title]")
                        if revised_date_element and revised_date_element.get("title"):
                            try:
                                revised_date = ScrapingHelper.get_first_value(
                                    revised_date_element.get("title")
                                )
                                if not revised_date:
                                    raise MissingDataException("改稿日が取得できませんでした。")
                                posted_at = datetime.strptime(
                                    revised_date.split(" ")[0], "%Y/%m/%d"
                                )  # 改稿日を解析
                                posted_at = LOCAL_TZ.localize(posted_at)
                            except ValueError:
                                posted_at = None  # 日付が取得できなかった場合はNoneを設定
                        else:
                            try:
                                # 改稿がなければ最初の投稿日を解析
                                posted_at = datetime.strptime(posted_at_text, "%Y/%m/%d")
                                posted_at = LOCAL_TZ.localize(posted_at)
                            except ValueError:
                                posted_at = None  # 日付が取得できなかった場合はNoneを設定
                    else:
                        posted_at = None  # 投稿日時が見つからない場合はNone

                    chapters.append(
                        Chapter(
                            title=title,
                            source_url="https://novel18.syosetu.com" + url,
                            posted_at=(
                                posted_at
                                if posted_at
                                else datetime(1970, 1, 1, 0, 0, 0, tzinfo=LOCAL_TZ)
                            ),
                        )
                    )

            # 次ページのリンクを取得
            next_page_element = soup.select_one(".c-pager__item--next")
            if next_page_element and next_page_element.get("href"):
                url = next_page_element.get("href")
                url = ScrapingHelper.get_first_value(url)
                if url is None:
                    raise MissingDataException("次のページURLが取得できませんでした。")
                # 次のページURLを設定
                current_url = "https://ncode.syosetu.com" + url
            else:
                # 次ページが無ければループを終了
                current_url = None

        if len(chapters) == 0:
            chapters.append(
                Chapter(
                    title=novel_metadata.title,
                    source_url=self.novel.source_url,
                    posted_at=novel_metadata.last_posted_at,
                )
            )
        return chapters

    def fetch_chapter_content(self, chapter_url: str) -> ChapterContent:
        """
        章の内容を取得する

        Args:
            chapter_url (str): 章のURL

        Returns:
            ChapterContent: 章の本文
        """
        response = NocturneHelper.request(chapter_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 章本文がある要素を特定
        content = soup.select_one(".p-novel__text:not(.p-novel__text--preface)")  # 小説本文のID
        if content:
            return ChapterContent(content=content.text.strip())
        else:
            return ChapterContent(content="コンテンツが見つかりませんでした")

    def extract_identifier_from_url(self, url: str) -> str:
        """
        URLから小説IDを抽出する
        """
        pattern = r"/(n[0-9a-zA-Z]+)/"

        match = re.search(pattern, url)

        return match.group(1) if match else ""
