from datetime import datetime
from sqlalchemy.orm import Session
from models.chapter_history_model import ChapterHistoryModel
from models.chapter_model import ChapterModel


class ChapterQueries:
    def __init__(self, session: Session):
        self.session = session

    def upsert_chapter(
        self,
        novel_id: int,
        title: str,
        content: str,
        source_url: str,
        posted_at: datetime,
    ):
        chapter = self.get_chapter_by_source_url(source_url)
        if chapter:
            history = ChapterHistoryModel(
                chapter_id=chapter.id,
                title=chapter.title,
                content=chapter.content,
                posted_at=chapter.posted_at,
            )
            self.session.add(history)
            self.session.flush()

            chapter.title = title
            chapter.content = content
            chapter.posted_at = posted_at
        else:

            chapter = ChapterModel(
                novel_id=novel_id,
                title=title,
                content=content,
                source_url=source_url,
                posted_at=posted_at,
            )
            self.session.add(chapter)
            self.session.flush()

        return chapter

    def get_novel_by_id(self, novel_id: int) -> list[ChapterModel] | None:
        return self.session.query(ChapterModel).filter(ChapterModel.novel_id == novel_id).all()

    def get_chapter_by_source_url(self, source_url
                                  : str) -> ChapterModel | None:
        return (
            self.session.query(ChapterModel)
            .filter(ChapterModel.source_url == source_url)
            .one_or_none()
        )
