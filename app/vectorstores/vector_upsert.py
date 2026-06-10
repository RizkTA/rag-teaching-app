import uuid
import gc
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):
        self.store = store
        self.batch_size = 8   # 🔥 smaller = safer for Render

    def upsert_chunks(self, chunks: List[Dict]):

        if not chunks:
            return {"inserted": 0, "status": "empty"}

        total_inserted = 0

        # PROCESS IN SMALL BATCHES
        for start in range(0, len(chunks), self.batch_size):

            batch = chunks[start:start + self.batch_size]

            texts = [c["text"] for c in batch]

            # 🔥 embed ONLY this batch (no inner batching!)
            vectors = embed_texts(texts)

            ids = []
            payloads = []

            for i, chunk in enumerate(batch):

                ids.append(chunk.get("id", str(uuid.uuid4())))

                payloads.append({
                    "text": chunk["text"],
                    "source": chunk.get("source", "unknown"),
                    "chunk_id": chunk.get("chunk_id", i),
                    "language": chunk.get("language", "auto"),
                    "topic": chunk.get("topic", "general"),
                    "metadata": chunk.get("metadata", {})
                })

            self.store.upsert(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )

            total_inserted += len(batch)

            # 🔥 CRITICAL MEMORY FIX
            del texts, vectors, ids, payloads, batch
            gc.collect()

        return {
            "inserted": total_inserted,
            "status": "success"
        }