from sqlalchemy.orm import Session

from models.search_tag_model import SearchTagModel
from repositories.queries.search_tag_queries import SearchTagQueries


class SearchTagService:
    def __init__(self, session: Session):
        self.session = session
        self.query = SearchTagQueries(session)

    def get_all(self) -> list[SearchTagModel]:
        return self.query.get_all()