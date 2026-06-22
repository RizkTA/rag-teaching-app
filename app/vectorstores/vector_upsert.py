from app.embeddings.embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):

        self.store = store

    def upsert_chunks(self, chunks):

        print("🔥 upsert_chunks start")
        print("upsert_chunks received", len(chunks), "chunks")
        # =================================
        # EMPTY CHECK
        # =================================
        if not chunks:

            print("⚠️ No chunks received")

            return {
                "status": "empty",
                "inserted": 0
            }

        # =================================
        # CLEAN CHUNKS
        # =================================
        valid_chunks = []
        texts = []

        for c in chunks:

            text = c.get("text")

            if text is None:
                continue

            if isinstance(text, list):
                text = " ".join(
                    map(str, text)
                )

            text = str(text).strip()

            if not text:
                continue

            texts.append(text)
            valid_chunks.append(c)

        if not texts:

            print("⚠️ No valid texts")

            return {
                "status": "empty_text",
                "inserted": 0
            }

        print(
            f"🔥 embedding {len(texts)} chunks"
        )

        # =================================
        # EMBEDDINGS
        # =================================


        import time

        t0 = time.time()

        print("Calling embed_texts")
        print("LEN(texts) =", len(texts))
        BATCH_SIZE = 16

        total_inserted = 0

        for i in range(0, len(valid_chunks), BATCH_SIZE):

            print(f"Processing batch {i // BATCH_SIZE + 1}")

            batch_chunks = valid_chunks[i:i + BATCH_SIZE]

            batch_texts = [
                str(c["text"]).strip()
                for c in batch_chunks
            ]

            print("Embedding", len(batch_texts), "texts")

            vectors = embed_texts(batch_texts)

            ids = []
            payloads = []

            for j, chunk in enumerate(batch_chunks):
                metadata = chunk.get("metadata", {})

                ids.append(chunk["id"])

                payloads.append({
                    "text": batch_texts[j],
                    "source": chunk.get("source", "unknown"),
                    "filename": metadata.get(
                        "filename",
                        chunk.get("source", "unknown")
                    ),
                    "chunk_id": chunk.get(
                        "chunk_id",
                        i + j
                    ),
                    "language": chunk.get(
                        "language",
                        "text"
                    ),
                    "topic": chunk.get(
                        "topic",
                        "general"
                    ),
                    "file_hash": metadata.get(
                        "file_hash"
                    ),
                    "is_code": metadata.get(
                        "is_code",
                        False
                    )
                })

            print("Upserting", len(ids), "vectors")

            self.store.upsert(
                ids,
                vectors,
                payloads
            )

            total_inserted += len(ids)

        print("🔥 qdrant complete")

        return {
            "status": "ok",
            "inserted": total_inserted
        }