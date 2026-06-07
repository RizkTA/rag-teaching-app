from sentence_transformers import SentenceTransformer


class LocalEmbedder:

    def __init__(self, model_name):

        self.model_name = model_name
        self.model = None

    def load_model(self):

        if self.model is None:

            self.model = SentenceTransformer(
                self.model_name
            )

    def embed(self, texts):

        self.load_model()

        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()