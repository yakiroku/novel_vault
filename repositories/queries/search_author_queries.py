from sqlalchemy.orm import Session
from models.search_author_model import SearchAuthorModel


class SearchAuthorQueries:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[SearchAuthorModel]:
        return self.session.query(SearchAuthorModel).all()
    
    def get_by_name(self, name: str) -> SearchAuthorModel:
        return self.session.query(SearchAuthorModel).filter_by(name=name).one_or_none()