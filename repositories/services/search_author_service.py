from sqlalchemy.orm import Session

from models.search_author_model import SearchAuthorModel
from repositories.queries.search_author_queries import SearchAuthorQueries


class SearchAuthorService:
    def __init__(self, session: Session):
        self.session = session
        self.query = SearchAuthorQueries(session)

    def get_all(self) -> list[SearchAuthorModel]:
        return self.query.get_all()
    
    def get_by_name(self, name: str) -> SearchAuthorModel:
        return self.query.get_by_name(name)