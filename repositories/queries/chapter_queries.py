from datetime import datetime
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from models.chapter_history_model import ChapterHistoryModel
from models.chapter_model import ChapterModel
from repositories.services.paragraph_service import ParagraphService


class ChapterQueries:
    def __init__(self, session: Session):
        self.session = session

    def upsert_chapter(
        self,
        novel_id: int,
        title: str,
        content: str,
        source_url: str,
        posted_at: datetime,
    ):

        paragragh_service = ParagraphService(session=self.session)

        chapter = self.get_chapter_by_source_url(source_url)
        if chapter:
            history = ChapterHistoryModel(
                chapter_id=chapter.id,
                title=chapter.title,
                content=paragragh_service.chapter_content(chapter_id=chapter.id),
                posted_at=chapter.posted_at,
            )
            # self.session.add(history)
            # self.session.flush()

            chapter.title = title
            chapter.posted_at = posted_at

            paragragh_service.delete_by_chapter_id(chapter_id=chapter.id)

        else:

            chapter = ChapterModel(
                novel_id=novel_id,
                title=title,
                source_url=source_url,
                posted_at=posted_at,
            )
            self.session.add(chapter)
            self.session.flush()

        # 章のテキストを50文字ごとに分割してParagraphModelに格納
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=0, separators=["。", "、", "．", "！", "？", "・"]
        )
        paragraphs = text_splitter.split_text(content)
        # model = SentenceTransformerSingleton.get_model()
        # embeddings = model.encode(paragraphs, show_progress_bar=False).tolist()
        # paragragh_service.batch_insert(
        #     chapter_id=chapter.id, contents=paragraphs, embeddings=embeddings
        # )
        paragragh_service.batch_insert(
            chapter_id=chapter.id, contents=paragraphs
        )

        return chapter

    def get_novel_by_id(self, novel_id: int) -> list[ChapterModel] | None:
        return self.session.query(ChapterModel).filter(ChapterModel.novel_id == novel_id).all()

    def get_chapter_by_source_url(self, source_url: str) -> ChapterModel | None:
        return (
            self.session.query(ChapterModel)
            .filter(ChapterModel.source_url == source_url)
            .one_or_none()
        )