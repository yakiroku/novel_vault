from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.paragraph_model import ParagraphModel
from util.sentence_transformer_singleton import SentenceTransformerSingleton


class ParagraphQueries:
    def __init__(self, session: Session):
        self.session = session

    def delete_by_chapter_id(
        self,
        chapter_id: int,
    ):
        self.session.query(ParagraphModel).filter(ParagraphModel.chapter_id == chapter_id).delete()
        self.session.flush()

    def chapter_content(self, chapter_id: int) -> list[ParagraphModel]:
        return (
            self.session.query(ParagraphModel).filter(ParagraphModel.chapter_id == chapter_id).order_by(ParagraphModel.id.asc()).all()
        )

    # def insert(self, chapter_id: int, content: str) -> ParagraphModel:
    #     # 各段落をベクトル化して保存

    #     model = SentenceTransformerSingleton.get_model()
    #     embedding = model.encode(content, show_progress_bar=False).tolist()  # 段落のベクトル化
    #     paragraph_model = ParagraphModel(
    #         chapter_id=chapter_id,
    #         content=content,
    #         embedding=embedding,
    #     )
    #     self.session.add(paragraph_model)
    #     self.session.flush()
    #     return paragraph_model

    def batch_insert(self, chapter_id: int, contents: list[str]):
        paragraph_models = []

        # 各段落とその埋め込みベクトルを組み合わせてモデルインスタンスを作成
        for content in contents:
            paragraph_model = ParagraphModel(
                chapter_id=chapter_id, content=content
            )
            paragraph_models.append(paragraph_model)

        # バッチ挿入処理
        self.session.add_all(paragraph_models)
        self.session.flush()  # 一度に挿入
