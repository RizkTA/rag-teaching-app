import uuid
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):
        self.store = store

    # ==============================
    # MAIN UPSERT FUNCTION
    # ==============================
    def upsert_chunks(self, chunks: List[Dict]):
        """
        Convert chunks → embeddings → store in Qdrant
        """

        if not chunks:
            return {"inserted": 0}

        texts = [c["text"] for c in chunks]

        # 1. Embed all chunks in batch (FAST)
        vectors = embed_texts(texts)

        ids = []
        payloads = []

        # 2. Build Qdrant payload
        for i, chunk in enumerate(chunks):

            ids.append(chunk.get("id", str(uuid.uuid4())))

            payloads.append({
                "text": chunk["text"],
                "source": chunk.get("source", "unknown"),
                "language": chunk.get("language", "auto"),
                "metadata": chunk.get("metadata", {}),
            })

        # 3. Upsert into Qdrant
        self.store.upsert(
            ids=ids,
            vectors=vectors,
            payloads=payloads
        )

        return {
            "inserted": len(chunks),
            "status": "success"
        }