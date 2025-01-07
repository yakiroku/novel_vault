from sqlalchemy.orm import Session
from models.tag_model import TagModel


class TagQueries:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, name: str) -> TagModel:
        tag = TagModel(name=name)
        self.session.add(tag)
        self.session.flush()

        return tag

    def get_by_name(self, name: str) -> TagModel | None:
        return self.session.query(TagModel).filter(TagModel.name == name).one_or_none()
