from app.embeddings.api_embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):
        self.store = store

    def upsert_chunks(self, chunks):

        print("🔥 upsert_chunks start")

        texts = [c["text"] for c in chunks]

        print("🔥 embedding texts:", len(texts))

        vectors = embed_texts(texts)

        print("🔥 embeddings done")

        ids = [c["id"] for c in chunks]

        payloads = [
            {
                "text": c["text"],
                "source": c.get("source"),
                "chunk_id": c.get("chunk_id"),
                "language": c.get("language"),
                "topic": c.get("topic"),
                "metadata": c.get("metadata", {})
            }
            for c in chunks
        ]

        print("🔥 qdrant upsert")

        self.store.upsert(ids, vectors, payloads)

        print("🔥 qdrant complete")

        return {
            "inserted": len(chunks),
            "status": "ok"
        }