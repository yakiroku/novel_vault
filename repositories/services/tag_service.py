from sqlalchemy.orm import Session
from models.tag_model import TagModel
from repositories.queries.tag_queries import TagQueries


class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.query = TagQueries(session)

    def insert(self, name: str) -> TagModel:
        return self.query.insert(name)

    def get_by_name(self, name: str) -> TagModel | None:
        return self.query.get_by_name(name)
