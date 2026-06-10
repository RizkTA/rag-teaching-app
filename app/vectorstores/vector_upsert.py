import uuid
import time
import gc
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):
        self.store = store
        self.batch_size = 16  # IMPORTANT: smaller for Render 512MB

    def upsert_chunks(self, chunks: List[Dict]):

        if not chunks:
            return {"inserted": 0, "status": "empty"}

        total_inserted = 0

        # =========================
        # PROCESS IN SMALL BATCHES
        # =========================
        for start in range(0, len(chunks), self.batch_size):

            batch = chunks[start:start + self.batch_size]

            print(f"Processing batch {start}-{start + len(batch)}")

            texts = [c["text"] for c in batch]

            # 🔥 SINGLE embedding call (NO nested loops)
            vectors = embed_texts(texts)

            ids = []
            payloads = []

            for chunk in batch:

                ids.append(chunk.get("id", str(uuid.uuid4())))

                payloads.append({
                    "text": chunk["text"],
                    "source": chunk.get("source", "unknown"),
                    "chunk_id": chunk.get("chunk_id", 0),
                    "language": chunk.get("language", "text"),
                    "topic": chunk.get("topic", "general"),
                    "metadata": chunk.get("metadata", {})
                })

            self.store.upsert(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )

            total_inserted += len(batch)

            # =========================
            # MEMORY CLEANUP (CRITICAL)
            # =========================
            del texts, vectors, ids, payloads, batch
            gc.collect()

            time.sleep(0.2)

        return {
            "inserted": total_inserted,
            "status": "success"
        }