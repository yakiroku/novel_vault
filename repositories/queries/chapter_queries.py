from datetime import datetime
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.chapter_history_model import ChapterHistoryModel
from models.chapter_model import ChapterModel
from repositories.services.paragraph_service import ParagraphService
from util.sentence_transformer_singleton import SentenceTransformerSingleton


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
            self.session.add(history)
            self.session.flush()

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
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
        paragraphs = text_splitter.split_text(content)
        model = SentenceTransformerSingleton.get_model()
        embeddings = model.encode(paragraphs, show_progress_bar=False).tolist()
        paragragh_service.batch_insert(chapter_id=chapter.id, contents=paragraphs, embeddings=embeddings)
            
        return chapter

    def get_novel_by_id(self, novel_id: int) -> list[ChapterModel] | None:
        return self.session.query(ChapterModel).filter(ChapterModel.novel_id == novel_id).all()

    def get_chapter_by_source_url(self, source_url
                                  : str) -> ChapterModel | None:
        return (
            self.session.query(ChapterModel)
            .filter(ChapterModel.source_url == source_url)
            .one_or_none()
        )


    def _split_into_paragraphs(self, text: str, max_length: int = 500) -> list[str]:
        """
        入力されたテキストを500文字ごとに分割しますが、句読点で自然に分割します。
        """
        sentences = re.split(r'([。．！？])', text)  # 句読点で分割
        paragraphs = []
        current_paragraph = ""

        for sentence in sentences:
            if len(current_paragraph) + len(sentence) > max_length:
                # 500文字を超える場合、現在の段落を追加して新しい段落を開始
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
            else:
                current_paragraph += sentence

        # 最後の段落が残っている場合
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())

        return paragraphs