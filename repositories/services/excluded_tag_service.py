from sqlalchemy.orm import Session

from models.excluded_tag_model import ExcludedTagModel
from repositories.queries.excluded_tag_queries import ExcludedTagQueries


class ExcludedTagService:
    def __init__(self, session: Session):
        self.session = session
        self.query = ExcludedTagQueries(session)

    def get_all(self) -> list[ExcludedTagModel]:
        return self.query.get_all()