from sentence_transformers import SentenceTransformer

class SentenceTransformerSingleton:
    _model = None

    @staticmethod
    def get_model():
        if SentenceTransformerSingleton._model is None:
            # モデルがまだロードされていない場合にのみロード
            SentenceTransformerSingleton._model = SentenceTransformer("msmarco-distilbert-base-v3")
            # SentenceTransformerSingleton._model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

        return SentenceTransformerSingleton._model