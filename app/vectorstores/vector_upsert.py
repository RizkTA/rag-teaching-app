import gc

from app.embeddings.api_embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):

        self.store = store

        self.batch_size = 4

    def upsert_chunks(self, chunks):

        inserted = 0

        for start in range(0, len(chunks), self.batch_size):

            batch = chunks[
                start:start + self.batch_size
            ]

            texts = [
                c["text"]
                for c in batch
            ]

            vectors = embed_texts(texts)

            ids = [
                c["id"]
                for c in batch
            ]

            payloads = []

            for c in batch:

                payloads.append({

                    "text": c["text"],

                    "source": c.get("source"),

                    "chunk_id": c.get("chunk_id"),

                    "language": c.get("language"),

                    "topic": c.get("topic"),

                    "metadata": c.get("metadata", {})
                })

            self.store.upsert(
                ids,
                vectors,
                payloads
            )

            inserted += len(batch)

            # MEMORY CLEANUP
            del texts
            del vectors
            del ids
            del payloads
            del batch

            gc.collect()

        return {
            "inserted": inserted,
            "status": "ok"
        }