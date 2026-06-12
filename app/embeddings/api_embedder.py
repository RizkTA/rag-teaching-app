_embedder = None


def get_embedder():

    global _embedder

    if _embedder is None:

        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    return _embedder


def embed_texts(texts):

    model = get_embedder()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=2
    )

    return embeddings.tolist()