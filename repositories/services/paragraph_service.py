from sqlalchemy.orm import Session

from models.chapter_model import ChapterModel
from models.paragraph_model import ParagraphModel
from repositories.queries.paragraph_queries import ParagraphQueries


class ParagraphService:
    def __init__(self, session: Session):
        self.session = session
        self.query = ParagraphQueries(session)

    def delete_by_chapter_id(self, chapter_id: int):
        self.query.delete_by_chapter_id(chapter_id=chapter_id)


    def chapter_content(self, chapter_id: int) -> str:
        """
        `chapter_id`に対応するChapterModelの内容を、分割された段落を元に1つの文章として再構成して返します。
        改行も維持されるようにします。
        """
        # ChapterModelから該当のchapterを取得
        chapter = self.session.query(ChapterModel).get(chapter_id)
        
        if chapter:
            # 段落の内容を取得
            paragraphs = self.session.query(ParagraphModel).filter_by(chapter_id=chapter.id).all()
            # 段落を改行を挟んで結合して元の文章に戻す
            full_content = "\n\n".join(paragraph.content for paragraph in paragraphs)
            return full_content
        
        return ""        

    def insert(self, chapter_id: int, content: str) -> ParagraphModel:
        return self.query.insert(chapter_id=chapter_id, content=content)


    def batch_insert(self, chapter_id: int, contents: list[str], embeddings: list[list[float]]):
        return self.query.batch_insert(chapter_id=chapter_id, contents=contents, embeddings=embeddings)