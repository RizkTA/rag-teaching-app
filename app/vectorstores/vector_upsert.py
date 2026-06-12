import gc

from app.embeddings.api_embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):
        self.store = store

    def upsert_chunks(self, chunks):

        batch_size = 8
        total = 0

        for start in range(0, len(chunks), batch_size):

            batch = chunks[start:start + batch_size]

            texts = [c["text"] for c in batch]

            vectors = embed_texts(texts)

            ids = [c["id"] for c in batch]

            payloads = [
                {
                    "text": c["text"],
                    "source": c.get("source"),
                    "chunk_id": c.get("chunk_id"),
                    "language": c.get("language"),
                    "topic": c.get("topic"),
                    "metadata": c.get("metadata", {})
                }
                for c in batch
            ]

            self.store.upsert(
                ids,
                vectors,
                payloads
            )

            total += len(batch)

            del texts
            del vectors
            del ids
            del payloads
            del batch

            gc.collect()

        return {
            "inserted": total,
            "status": "ok"
        }