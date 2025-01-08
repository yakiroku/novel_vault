from datetime import datetime
from sqlalchemy.orm import Session

from models.novel_model import NovelModel
from repositories.queries.novel_queries import NovelQueries
from shared.schemas.novel_metadata import NovelMetadata
from shared.schemas.novel_summary import NovelSummary


class NovelService:
    def __init__(self, session: Session):
        self.session = session
        self.query = NovelQueries(session)

    def update(self, source_url: str, novel_metadata: NovelMetadata) -> NovelModel | None:
        return self.query.update(
            source_url=source_url,
            title=novel_metadata.title,
            author=novel_metadata.author,
            description=novel_metadata.description,
            tags=novel_metadata.tags,
            last_posted_at=novel_metadata.last_posted_at,
        )

    def upsert_novel_list(self, novel_list: list[NovelSummary]):
        # 既存の小説リストを一括取得
        existing_novels = self.session.query(NovelModel).all()

        # source_url をキーとする辞書を作成（高速な検索のため）
        existing_novels_map = {novel.source_url: novel for novel in existing_novels}

        # 入力リストを処理
        for novel in novel_list:
            # すでに存在している場合はスキップ
            if novel.source_url in existing_novels_map:
                continue

            # 存在しない場合は新規挿入
            novel_model = self.query.insert(
                title=novel.title,
                author="",
                description="",
                tags=[],
                last_posted_at=datetime.min,
                source_url=novel.source_url,
                site=novel.site.value,
            )

            # 新規挿入した小説を辞書に追加
            existing_novels_map[novel.source_url] = novel_model

    def get_novel_list(self) -> list[NovelModel]:
        return self.query.get_novel_list()

    def exclude_novel(self, novel_id: int) -> None:
        """
        指定された小説を除外する。

        :param session: データベースセッション
        :param novel_id: 除外する小説のID
        """
        self.query.exclude_novel(novel_id)

    def delete_novel(self, novel_id: int) -> None:
        """
        指定された小説を削除する。

        :param session: データベースセッション
        :param novel_id: 削除する小説のID
        """
        self.query.delete_novel(novel_id)
