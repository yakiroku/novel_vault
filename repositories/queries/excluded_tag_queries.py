from sqlalchemy.orm import Session
from models.excluded_tag_model import ExcludedTagModel


class ExcludedTagQueries:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ExcludedTagModel]:
        return self.session.query(ExcludedTagModel).all()
