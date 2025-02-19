import logging
from dotenv import load_dotenv

from db.db_session_manager import DBSessionManager
from repositories.services.chapter_service import ChapterService
from repositories.services.excluded_tag_service import ExcludedTagService
from repositories.services.novel_service import NovelService
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
    nocturne_weekly_tag_search = NovelSearchFactory.create_searcher(
        SearchTarget.NOCTURNE_WEEKLY_TAG
    )
    logger.info("ノクターンタグWEEK検索を実行中...")
    nocturne_weekly_tag_search_list = nocturne_weekly_tag_search.fetch_novel_list()
    logger.info(
        f"ノクターンタグWEEK検索で {len(nocturne_weekly_tag_search_list)} 件の小説を取得しました。"
    )

    # ノクターン作者検索
    nocturne_author_search = NovelSearchFactory.create_searcher(
        SearchTarget.NOCTURNE_AUTHOR
    )
    logger.info("ノクターン作者検索を実行中...")
    nocturne_author_search_list = nocturne_author_search.fetch_novel_list()
    logger.info(
        f"ノクターン作者検索で {len(nocturne_author_search_list)} 件の小説を取得しました。"
    )
    # # PIXIVタグ検索
    # pixiv_tag_search = NovelSearchFactory.create_searcher(SearchTarget.PIXIV_TAG)
    # logger.info("PIXIVタグ検索を実行中...")
    # pixiv_tag_search_list = pixiv_tag_search.fetch_novel_list()
    # logger.info(f"PIXIVタグ検索で {len(pixiv_tag_search_list)} 件の小説を取得しました。")

    # カクヨム検索
    kakuyomu_tag_search = NovelSearchFactory.create_searcher(
        SearchTarget.KAKUYOMU_TAG
    )
    logger.info("カクヨム検索を実行中...")
    kakuyomu_tag_search_list = kakuyomu_tag_search.fetch_novel_list()
    logger.info(
        f"カクヨム検索で {len(kakuyomu_tag_search_list)} 件の小説を取得しました。"
    )
    all_novels = []
    all_novels.extend(nocturne_ranked_search_list)
    all_novels.extend(nocturne_tag_search_list)
    all_novels.extend(nocturne_weekly_tag_search_list)
    all_novels.extend(nocturne_author_search_list)
    all_novels.extend(kakuyomu_tag_search_list)

    # ノベルリストのアップサート
    with DBSessionManager.auto_commit_session() as session:
        novel_service = NovelService(session)
        _ = novel_service.get_check_novel_list()
        novel_service.upsert_novel_list(all_novels)
        logger.info("ノベルリストをデータベースにアップサートしました。")

    # 小説の詳細を更新し、章を処理
    with DBSessionManager.auto_commit_session() as session:
        novel_service = NovelService(session)
        chapter_service = ChapterService(session)
        excluded_tag_service = ExcludedTagService(session)
        novel_list = novel_service.get_check_novel_list()
        logger.info(f"{len(novel_list)} 件の小説がデータベースにあります。")

        excluded_tags = excluded_tag_service.get_all()

        for novel_index, novel in enumerate(novel_list, start=1):
            scraper = ScraperFactory.create_scraper(novel)
            novel_metadata = scraper.fetch_novel_metadata()
            if novel_metadata is None:
                novel_service.delete_novel(novel.id)
                logger.info(f"({novel_index}/{len(novel_list)}) 小説 {novel.title} を除外します。")
                continue
            if excluded_tags is not None:
                excluded_flg = False
                for excluded_tag in excluded_tags:
                    # excluded_tag.nameがnovel_metadata.tagsのどれかに部分一致する場合
                    for tag in novel_metadata.tags:
                        if excluded_tag.name in tag:
                            # 部分一致した場合にログを出力
                            novel_service.exclude_novel(novel.id)
                            logger.info(
                                f"({novel_index}/{len(novel_list)}) 小説 {novel.title} のタグ '{tag}' が除外タグ '{excluded_tag.name}' と部分一致しました。"
                            )
                            # 小説の処理をスキップして次の小説に進む
                            excluded_flg = True
                            break

                if excluded_flg == True:
                    continue

            if novel.completed != novel_metadata.completed:
                novel_service.update_completed(novel.source_url, novel_metadata.completed)
                logger.info(
                    f"({novel_index}/{len(novel_list)}) 小説 {novel.title} の完了状態を{novel_metadata.completed}に更新しました。"
                )

            if novel.last_posted_at.astimezone(LOCAL_TZ) >= novel_metadata.last_posted_at:
                logger.info(
                    f"({novel_index}/{len(novel_list)}) {novel.title}は未更新のためスキップします。"
                )
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
                if (
                    chapter_model
                    and chapter_model.posted_at.astimezone(LOCAL_TZ) >= chapter.posted_at
                ):
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
