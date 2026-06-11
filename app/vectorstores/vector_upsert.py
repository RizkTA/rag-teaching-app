import uuid
import gc

class VectorUpsert:

    def __init__(self, store):
        self.store = store
        self.batch_size = 16  # safe for Render

    def upsert_chunks(self, chunks):

        if not chunks:
            return {"inserted": 0}

        total = 0

        # process small batches
        for i in range(0, len(chunks), self.batch_size):

            batch = chunks[i:i + self.batch_size]

            texts = [c["text"] for c in batch]

            vectors = embed_texts(texts)

            ids = [c.get("id", str(uuid.uuid4())) for c in batch]

            payloads = [
                {
                    "text": c["text"],
                    "source": c.get("source", ""),
                    "chunk_id": c.get("chunk_id", 0),
                    "language": c.get("language", "auto"),
                    "topic": c.get("topic", "general"),
                }
                for c in batch
            ]

            self.store.upsert(ids, vectors, payloads)

            total += len(batch)

            # 🔥 CRITICAL MEMORY CLEANUP
            del batch, texts, vectors, ids, payloads
            gc.collect()

        return {"inserted": total}