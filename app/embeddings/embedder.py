from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedder():

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


def embed_texts(texts):

    model = get_embedder()

    return model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()