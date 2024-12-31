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

    def update(self, source_url: str, novel_metadata: NovelMetadata):
        self.query.update(
            source_url=source_url,
            title=novel_metadata.title,
            author=novel_metadata.author,
            description=novel_metadata.description,
            last_posted_at=novel_metadata.last_posted_at,
        )

    def upsert_novel_list(self, novel_list: list[NovelSummary]):
        for novel in novel_list:
            if not self.query.get_nobel_by_source_url(novel.source_url):
                self.query.insert(
                    title=novel.title,
                    author="",
                    description="",
                    last_posted_at=datetime.min,
                    source_url=novel.source_url,
                    site=novel.site.value,
                )

    def get_novel_list(self) -> list[NovelModel]:
        return self.query.get_novel_list()
