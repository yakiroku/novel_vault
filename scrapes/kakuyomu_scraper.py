from datetime import datetime
import json
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


class KakuyomuScraper(NovelScraperInterface):
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

        # タイトルを抽出
        title_tag = soup.find("h1", class_="Heading_heading__lQ85n")
        title = title_tag.get_text(strip=True) if title_tag else "タイトルなし"

        # 作者名を抽出
        author_tag = soup.find("div", class_="partialGiftWidgetActivityName")
        author = author_tag.get_text(strip=True) if author_tag else "作者名なし"

        # 概要を抽出
        summary_tag = soup.find("div", class_="CollapseTextWithKakuyomuLinks_collapseText__XSlmz")
        description = summary_tag.get_text(" ", strip=True) if summary_tag else "概要なし"

        # <script>タグを全て取得
        scripts = soup.find_all("script")

        # "tagLabels"を含む<script>タグを検索
        for script in scripts:
            if script.string:  # <script>タグの中身が空でない場合
                # 正規表現で"tagLabels"の内容を探す
                match = re.search(r'"tagLabels":\s*\[(.*?)\]', script.string)
                if match:
                    # "tagLabels"の値を取り出して、カンマ区切りでリストにする
                    tags = json.loads("[" + match.group(1) + "]")
                    break
            
        # 最終更新日時を抽出
        last_updated_tag = soup.find("time")

        # datetime型に変換
        try:
            if last_updated_tag and isinstance(last_updated_tag, Tag):
                # datetime属性を取得
                datetime_attr = last_updated_tag.get("datetime")
                if datetime_attr:
                    datetime_str = ScrapingHelper.get_first_value(datetime_attr) or ""
                    # ISO 8601形式をUTCで解析
                    last_posted_at_datetime = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    # UTCからローカルタイムに変換
                    last_posted_at_datetime = last_posted_at_datetime.astimezone(LOCAL_TZ)
                else:
                    raise ValueError("datetime属性が見つかりませんでした")
            else:
                raise ValueError("最終更新日時のタグが見つかりませんでした")
        except ValueError:
            # フォーマットが不正な場合のデフォルト値
            last_posted_at_datetime = datetime(1970, 1, 1, 0, 0, 0, tzinfo=LOCAL_TZ)

        # 執筆状況を抽出
        status_tag = soup.find("dt", text="執筆状況")
        if status_tag:
            tag = status_tag.find_next_sibling("dd")
            if tag is not None:
                status = tag.get_text(strip=True)
        else:
            status = "完結状態なし"

        # 完結済かどうかの判定
        completed = (status == "完結済")

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

        response = NocturneHelper.request(current_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # <script>タグ内からEpisode情報を抽出
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string:
                # 正規表現で"Episode"のデータを取得
                matches = re.findall(r'"Episode:(\d+)":\{.*?"id":"(\d+)".*?"title":"(.*?)".*?"publishedAt":"(.*?)".*?\}', script.string)
                for match in matches:
                    _, episode_id, episode_title, published_at = match
                    try:
                        published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")  # ISO 8601形式
                        published_at = LOCAL_TZ.localize(published_at)
                    except ValueError:
                        published_at = None  # 日付が取得できなかった場合はNone
                    chapters.append(
                        Chapter(
                            title=episode_title,
                            source_url=f"{self.novel.source_url}/episodes/{episode_id}",
                            posted_at=published_at or datetime(1970, 1, 1, 0, 0, 0, tzinfo=LOCAL_TZ)
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
        content = soup.select_one(".widget-episodeBody")  # 小説本文のID
        if content:
            return ChapterContent(content=content.text.strip())
        else:
            return ChapterContent(content="コンテンツが見つかりませんでした")