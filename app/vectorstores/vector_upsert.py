import uuid
import gc
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):
        self.store = store
        self.batch_size = 8   # safe for Render 512MB

    def upsert_chunks(self, chunks: List[Dict]):

        if not chunks:
            return {"inserted": 0, "status": "empty"}

        total_inserted = 0

        for start in range(0, len(chunks), self.batch_size):

            batch = chunks[start:start + self.batch_size]

            texts = [c["text"] for c in batch]

            vectors = embed_texts(texts)

            ids = []
            payloads = []

            for i, chunk in enumerate(batch):

                ids.append(chunk.get("id", str(uuid.uuid4())))

                payloads.append({
                    "text": chunk["text"],
                    "source": chunk.get("source", "unknown"),
                    "chunk_id": chunk.get("chunk_id", i),
                    "language": chunk.get("language", "text"),
                    "topic": chunk.get("topic", "general"),
                    "metadata": chunk.get("metadata", {})
                })

            # UPSERT
            self.store.upsert(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )

            total_inserted += len(batch)

            # 🔥 MEMORY CLEANUP (IMPORTANT FOR RENDER)
            del texts, vectors, ids, payloads, batch
            gc.collect()

        return {
            "inserted": total_inserted,
            "status": "success"
        }