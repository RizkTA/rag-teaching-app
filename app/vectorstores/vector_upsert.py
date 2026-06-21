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
        print("STEP A")
        #vectors = embed_texts(texts)
        print("STEP A")

        import time

        t0 = time.time()

        print("Calling embed_texts")
        print("LEN(texts) =", len(texts))
        vectors = embed_texts(texts)
        print(
            "embed_texts returned in",
            time.time() - t0,
            "seconds"
        )
        print("STEP B")
        print("STEP B")
        if vectors is None:

            raise Exception(
                "embed_texts returned None"
            )

        if len(vectors) == 0:

            raise Exception(
                "No embeddings generated"
            )

        print(
            f"🔥 embeddings generated: {len(vectors)}"
        )

        # =================================
        # SAFETY CHECK
        # =================================
        if len(vectors) != len(valid_chunks):

            raise Exception(
                f"Vector count mismatch "
                f"({len(vectors)} vs {len(valid_chunks)})"
            )

        # =================================
        # BUILD IDS + PAYLOADS
        # =================================
        ids = []
        payloads = []

        for idx, chunk in enumerate(valid_chunks):

            metadata = chunk.get(
                "metadata",
                {}
            )

            ids.append(
                chunk["id"]
            )

            payloads.append({
                "text": texts[idx],

                "source": chunk.get(
                    "source",
                    "unknown"
                ),

                "filename": metadata.get(
                    "filename",
                    chunk.get("source", "unknown")
                ),

                "chunk_id": chunk.get(
                    "chunk_id",
                    idx
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
                ),

                # ADD THIS
                "embedding": vectors[idx]
            })


        print(
            f"🔥 upserting {len(ids)} vectors"
        )

        # =================================
        # UPSERT
        # =================================
        self.store.upsert(
            ids,
            vectors,
            payloads
        )

        print("🔥 qdrant complete")

        return {

            "status": "ok",

            "inserted":
                len(payloads)
        }