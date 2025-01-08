import os
import logging
from dotenv import load_dotenv

from db.db_session_manager import DBSessionManager
from repositories.services.chapter_service import ChapterService
from repositories.services.novel_service import NovelService
from scrapes.pdf_scraper import PdfScraper
from scrapes.scraper_factory import ScraperFactory
from search.novel_search_factory import NovelSearchFactory
from settings import LOCAL_TZ
from shared.enums.search_target import SearchTarget

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("小説の検索を開始します。")
    # ノクターンランク検索
    nocturne_ranked_search = NovelSearchFactory.create_searcher(SearchTarget.NOCTURNE_RANKED)
    logger.info("ノクターンランク検索を実行中...")
    nocturne_ranked_search_list = nocturne_ranked_search.fetch_novel_list()
    logger.info(
        f"ノクターンランク検索で {len(nocturne_ranked_search_list)} 件の小説を取得しました。"
    )

    # ノクターンタグ検索
    nocturne_tag_search = NovelSearchFactory.create_searcher(SearchTarget.NOCTURNE_TAG)
    logger.info("ノクターンタグ検索を実行中...")
    nocturne_tag_search_list = nocturne_tag_search.fetch_novel_list()
    logger.info(f"ノクターンタグ検索で {len(nocturne_tag_search_list)} 件の小説を取得しました。")

    # ノクターンWEEKタグ検索
    nocturne_weekly_tag_search = NovelSearchFactory.create_searcher(SearchTarget.NOCTURNE_WEEKLY_TAG)
    logger.info("ノクターンタグWEEK検索を実行中...")
    nocturne_weekly_tag_search_list = nocturne_weekly_tag_search.fetch_novel_list()
    logger.info(f"ノクターンタグWEEK検索で {len(nocturne_weekly_tag_search_list)} 件の小説を取得しました。")

    # PIXIVタグ検索
    # pixiv_tag_search = NovelSearchFactory.create_searcher(SearchTarget.PIXIV_TAG)
    # logger.info("PIXIVタグ検索を実行中...")
    # pixiv_tag_search_list = pixiv_tag_search.fetch_novel_list()
    # logger.info(f"PIXIVタグ検索で {len(pixiv_tag_search_list)} 件の小説を取得しました。")

    all_novels = []
    all_novels.extend(nocturne_ranked_search_list)
    all_novels.extend(nocturne_tag_search_list)
    all_novels.extend(nocturne_weekly_tag_search_list)

    # ノベルリストのアップサート
    with DBSessionManager.auto_commit_session() as session:
        novel_service = NovelService(session)
        _ = novel_service.get_novel_list()
        novel_service.upsert_novel_list(all_novels)
        logger.info("ノベルリストをデータベースにアップサートしました。")

    # 小説の詳細を更新し、章を処理
    with DBSessionManager.auto_commit_session() as session:
        novel_service = NovelService(session)
        chapter_service = ChapterService(session)
        novel_list = novel_service.get_novel_list()
        logger.info(f"{len(novel_list)} 件の小説がデータベースにあります。")

        for novel_index, novel in enumerate(novel_list, start=1):
            scraper = ScraperFactory.create_scraper(novel)
            novel_metadata = scraper.fetch_novel_metadata()
            if novel_metadata is None:
                novel_service.delete_novel(novel.id)
                logger.info(f"({novel_index}/{len(novel_list)}) 小説 {novel.title} を除外します。")
                continue
            if novel.last_posted_at.replace(tzinfo=LOCAL_TZ) >= novel_metadata.last_posted_at:
                # logger.info(f"({novel_index}/{len(novel_list)}) {novel.title}は未更新のためスキップします。")
                continue
            novel_service.update(novel.source_url, novel_metadata)
            logger.info(
                f"({novel_index}/{len(novel_list)}) 小説 {novel.title} のメタデータを更新しました。"
            )

            logger.info(f"小説 {novel.title} の章を処理中...")
            chapter_list = scraper.fetch_chapter_list(novel_metadata)
            logger.info(f"小説 {novel.title} で {len(chapter_list)} 件の章が見つかりました。")
            chapter_model_list = chapter_service.get_novel_by_id(novel.id)
            if chapter_model_list is None:
                chapter_model_list = []

            for chapter_index, chapter in enumerate(chapter_list, start=1):
                # logger.info(f"  ({chapter_index}/{len(chapter_list)}) 章 {chapter.title} を処理中...")
                # chapter_model_listからchapter_ref_idが一致するものを探す
                chapter_model = next(
                    (
                        chapter_model
                        for chapter_model in chapter_model_list
                        if chapter_model.source_url == chapter.source_url
                    ),
                    None,
                )
                if chapter_model and chapter_model.posted_at >= chapter.posted_at:
                    # logger.info(f"未更新のためスキップします。")
                    continue
                chapter_content = scraper.fetch_chapter_content(chapter.source_url)
                chapter_service.upsert(
                    novel_id=novel.id, chapter=chapter, chapter_content=chapter_content
                )
                logger.info(
                    f"({novel_index}/{len(novel_list)}):({chapter_index}/{len(chapter_list)}) {chapter.title} をデータベースにアップサートしました。"
                )
            session.commit()

    logger.info("すべての処理が完了しました。")


if __name__ == "__main__":
    # 環境変数の読み込み
    # os.environ.clear()
    load_dotenv(".env", override=True)

    logger.info("処理を開始します。")
    main()
    # pdf = PdfScraper()
    # # pdf.fetch_chapter_content(is_vertical=True)
    # text = pdf.process_images_to_chapters('/Users/test/Documents/novel/小説データ/主導/本文/skebのコピー/')
    # print(text)