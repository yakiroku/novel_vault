from sqlalchemy.orm import Session

from models.novel_tag_model import NovelTagModel
from repositories.queries.novel_tag_queries import NovelTagQueries

class NovelTagService:
    def __init__(self, session: Session):
        self.session = session
        self.query = NovelTagQueries(session)

    def insert(self, novel_id: int, tag_id: int) -> NovelTagModel:
        return self.query.insert(novel_id=novel_id, tag_id=tag_id)
