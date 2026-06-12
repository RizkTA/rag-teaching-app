_store = None
_embedder = None
_reranker = None


# =========================
# QDRANT STORE (LAZY)
# =========================
def get_store():
    global _store
    if _store is None:
        from app.vectorstores.qdrant_store import QDRantStore
        from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM

        _store = QDRantStore(
            QDRANT_URL,
            QDRANT_COLLECTION,
            EMBED_DIM
        )
    return _store


# =========================
# EMBEDDER (LAZY)
# =========================
def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def embed_texts(texts):
    model = get_embedder()
    return model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=2
    ).tolist()


# =========================
# RERANKER (LAZY)
# =========================
def get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker
