import uuid
import gc
from app.embeddings.api_embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):
        self.store = store
        self.batch_size = 8   # safe for 512MB

    def upsert_chunks(self, chunks):

        if not chunks:
            return {"inserted": 0}

        total = 0

        for i in range(0, len(chunks), self.batch_size):

            batch = chunks[i:i + self.batch_size]

            texts = [c["text"] for c in batch]

            # 🔥 SINGLE EMBED CALL ONLY
            vectors = embed_texts(texts)

            ids = []
            payloads = []

            for j, c in enumerate(batch):

                ids.append(c.get("id", str(uuid.uuid4())))

                payloads.append({
                    "text": c["text"],
                    "source": c.get("source", "unknown"),
                    "chunk_id": c.get("chunk_id", j),
                    "language": c.get("language", "text"),
                    "topic": c.get("topic", "general"),
                    "metadata": c.get("metadata", {})
                })

            self.store.upsert(ids, vectors, payloads)

            total += len(batch)

            # 🔥 MEMORY CONTROL (CRITICAL FOR RENDER)
            del texts, vectors, ids, payloads, batch
            gc.collect()

        return {"inserted": total}