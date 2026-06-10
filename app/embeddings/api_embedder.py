from sentence_transformers import SentenceTransformer

# ==============================
# LAZY LOAD MODEL (IMPORTANT)
# ==============================
embedder = None


def get_embedder():
    global embedder

    if embedder is None:
        embedder = SentenceTransformer(
            "BAAI/bge-base-en-v1.5"
        )

    return embedder


# ==============================
# EMBED TEXTS
# ==============================
def embed_texts(texts):

    model = get_embedder()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()
