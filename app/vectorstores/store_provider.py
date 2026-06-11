# app/vectorstores/store_provider.py

from functools import lru_cache
from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM


@lru_cache(maxsize=1)
def get_store():
    """
    Lazy singleton Qdrant store.
    Only created when first used (NOT at startup).
    Prevents Render OOM crashes.
    """

    from app.vectorstores.qdrant_store import QdrantStore

    return QdrantStore(
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embed_dim=EMBED_DIM
    )