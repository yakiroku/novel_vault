from sqlalchemy.orm import Session
from models.search_tag_model import SearchTagModel


class SearchTagQueries:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[SearchTagModel]:
        return self.session.query(SearchTagModel).all()
