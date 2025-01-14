from datetime import datetime
from sqlalchemy.orm import Session
from models.novel_model import NovelModel
from repositories.services.novel_tag_service import NovelTagService
from repositories.services.tag_service import TagService


class NovelQueries:
    def __init__(self, session: Session):
        self.session = session

    def update(
        self,
        source_url: str,
        title: str,
        author: str,
        tags: list[str],
        description: str,
        last_posted_at: datetime,
    ) -> NovelModel | None:
        novel = self.get_nobel_by_source_url(source_url)
        if novel:
            # タグを同期
            self._sync_tags(novel, tags)
            novel.title = title
            novel.author = author
            novel.description = description
            novel.last_posted_at = last_posted_at

        return novel

    def insert(
        self,
        title: str,
        author: str,
        description: str,
        tags: list[str],
        last_posted_at: datetime,
        source_url: str,
        site: str,
    ):
        novel = NovelModel(
            title=title,
            author=author,
            description=description,
            site=site,
            last_posted_at=last_posted_at,
            source_url=source_url,
        )
        self.session.add(novel)
        self.session.flush()
        # タグを同期
        self._sync_tags(novel, tags)
        return novel

    def get_nobel_by_source_url(self, source_url: str) -> NovelModel | None:
        return (
            self.session.query(NovelModel).filter(NovelModel.source_url == source_url).one_or_none()
        )

    def get_check_novel_list(self) -> list[NovelModel]:
        return (
            self.session.query(NovelModel)
            .filter(
                NovelModel.excluded == False,
                NovelModel.deleted == False,
                NovelModel.completed == False,
            )
            .order_by(NovelModel.last_posted_at.desc())
            .all()
        )

    def exclude_novel(self, novel_id: int) -> None:
        novel = self.session.get(NovelModel, novel_id)
        if novel:
            novel.excluded = True

    def delete_novel(self, novel_id: int) -> None:
        novel = self.session.get(NovelModel, novel_id)
        if novel:
            novel.deleted = True

    # タグ処理を共通化したメソッド
    def _sync_tags(self, novel: NovelModel, tags: list[str]):
        """
        小説に紐づけられるタグを同期する
        """
        # 現在のタグを取得（タグ名 -> NovelTagModel の辞書）
        current_tags = {tag.tag.name: tag for tag in novel.novel_tags}
        new_tags = []

        tag_service = TagService(self.session)
        novel_tag_service = NovelTagService(self.session)
        for tag_name in tags:
            if tag_name in current_tags:
                # 既存のタグを再利用
                new_tags.append(current_tags[tag_name])
            else:
                # 新規タグを作成
                tag_model = tag_service.get_by_name(tag_name)
                if not tag_model:
                    new_tag = tag_service.insert(
                        tag_name
                    )  # 新しく追加されたタグのIDを取得可能にする
                else:
                    new_tag = tag_model

                # 新しいタグと小説を関連付ける
                novel_tag = novel_tag_service.insert(novel_id=novel.id, tag_id=new_tag.id)
                new_tags.append(novel_tag)

        # 削除すべきタグを中間テーブルから削除
        for current_tag in novel.novel_tags:
            if current_tag.tag.name not in tags:
                self.session.delete(current_tag)

        # novelのtagsを更新
        novel.novel_tags = new_tags  # 中間テーブルを通じて更新されたタグリストをセット
