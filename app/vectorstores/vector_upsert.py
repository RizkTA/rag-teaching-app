import uuid
import time
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):
        self.store = store
        self.embed_batch_size = 16   # safe for API
        self.chunk_batch_size = 32   # safe for memory

    # ======================================
    # MAIN UPSERT (CLEAN + SAFE)
    # ======================================
    def upsert_chunks(self, chunks: List[Dict]):

        if not chunks:
            return {"inserted": 0, "status": "empty"}

        total_inserted = 0

        # ======================================
        # STEP 1: PROCESS CHUNKS IN SMALL GROUPS
        # ======================================
        for start in range(0, len(chunks), self.chunk_batch_size):

            batch_chunks = chunks[start:start + self.chunk_batch_size]

            texts = [c["text"] for c in batch_chunks]

            print(f"🚀 Embedding batch {start}-{start + len(batch_chunks)}")

            # ======================================
            # STEP 2: EMBEDDINGS (SAFE BATCHING)
            # ======================================
            vectors = []

            for i in range(0, len(texts), self.embed_batch_size):

                sub_batch = texts[i:i + self.embed_batch_size]

                vecs = embed_texts(sub_batch)

                vectors.extend(vecs)

                time.sleep(0.2)  # avoid rate limits

            # ======================================
            # STEP 3: BUILD PAYLOADS
            # ======================================
            ids = []
            payloads = []

            for i, chunk in enumerate(batch_chunks):

                ids.append(chunk.get("id", str(uuid.uuid4())))

                payloads.append({
                    "text": chunk["text"],
                    "source": chunk.get("source", "unknown"),
                    "chunk_id": chunk.get("chunk_id", i),
                    "language": chunk.get("language", "text"),
                    "topic": chunk.get("topic", "general"),
                    "metadata": chunk.get("metadata", {})
                })

            # ======================================
            # STEP 4: UPSERT TO QDRANT
            # ======================================
            self.store.upsert(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )

            total_inserted += len(batch_chunks)

            print(f"✅ Inserted {len(batch_chunks)} chunks")

        return {
            "inserted": total_inserted,
            "status": "success"
        }