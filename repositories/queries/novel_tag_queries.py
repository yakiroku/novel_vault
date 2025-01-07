from sqlalchemy.orm import Session
from models.novel_tag_model import NovelTagModel


class NovelTagQueries:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, novel_id: int, tag_id: int) -> NovelTagModel:
        novel_tag = NovelTagModel(novel_id=novel_id, tag_id=tag_id)
        self.session.add(novel_tag)
        self.session.flush()

        return novel_tag
