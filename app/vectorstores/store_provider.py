from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


_store = None

def get_store():
    global _store
    if _store is None:
        from app.vectorstores.qdrant_store import QdrantStore
        from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM

        _store = QdrantStore(
            QDRANT_URL,
            QDRANT_COLLECTION,
            EMBED_DIM
        )

    return _store