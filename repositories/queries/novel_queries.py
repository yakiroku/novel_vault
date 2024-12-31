from datetime import datetime
from sqlalchemy.orm import Session
from models.novel_model import NovelModel


class NovelQueries:
    def __init__(self, session: Session):
        self.session = session

    def update(
        self,
        source_url: str,
        title: str,
        author: str,
        description: str,
        last_posted_at: datetime,
    ):
        novel = self.get_nobel_by_source_url(source_url)
        if novel:
            novel.title = title
            novel.author = author
            novel.description = description
            novel.last_posted_at = last_posted_at

    def insert(
        self,
        title: str,
        author: str,
        description: str,
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

        return novel

    def get_nobel_by_source_url(self, source_url: str) -> NovelModel | None:
        return (
            self.session.query(NovelModel).filter(NovelModel.source_url == source_url).one_or_none()
        )

    def get_novel_list(self) -> list[NovelModel]:
        return self.session.query(NovelModel).filter(NovelModel.excluded == False).all()

    def exclude_novel(self, novel_id: int) -> None:
        novel = self.session.get(NovelModel, novel_id)
        if novel:
            novel.excluded = True