from functools import lru_cache

@lru_cache(maxsize=1)
def get_store():

    from app.vectorstores.qdrant_store import QdrantStore
    from app.config import (
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

    return QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )