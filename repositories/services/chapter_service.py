from datetime import datetime
from sqlalchemy.orm import Session

from models.chapter_model import ChapterModel
from models.novel_model import NovelModel
from repositories.queries.chapter_queries import ChapterQueries
from repositories.queries.novel_queries import NovelQueries
from shared.schemas.chapter import Chapter
from shared.schemas.chapter_content import ChapterContent
from shared.schemas.novel_summary import NovelSummary


class ChapterService:
    def __init__(self, session: Session):
        self.session = session
        self.query = ChapterQueries(session)

    def upsert(self, novel_id: int, chapter: Chapter, chapter_content: ChapterContent):
        self.query.upsert_chapter(
            novel_id=novel_id,
            title=chapter.title,
            content=chapter_content.content,
            source_url=chapter.source_url,
            posted_at=chapter.posted_at,
        )

    def get_novel_by_id(self, novel_id: int) -> list[ChapterModel] | None:
        return self.query.get_novel_by_id(novel_id)

    def get_chapter_by_source_url(self, source_url: str) -> ChapterModel | None:
        return self.query.get_chapter_by_source_url(source_url)
