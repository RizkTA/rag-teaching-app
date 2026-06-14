from app.embeddings.embedder import embed_texts


class VectorUpsert:

    def __init__(self, store):

        self.store = store

    def upsert_chunks(self, chunks):

        print("🔥 upsert_chunks start")

        # =================================
        # EMPTY CHECK
        # =================================
        if not chunks:

            print("⚠️ No chunks received")

            return {
                "inserted": 0,
                "status": "empty"
            }

        # =================================
        # PREPARE TEXTS
        # =================================
        texts = []

        valid_chunks = []

        for c in chunks:

            text = c.get("text", "")

            if text is None:
                continue

            # flatten lists
            if isinstance(text, list):
                text = " ".join(map(str, text))

            text = str(text).strip()

            # skip empty
            if not text:
                continue

            texts.append(text)

            valid_chunks.append(c)

        # no valid text
        if not texts:

            print("⚠️ No valid texts")

            return {
                "inserted": 0,
                "status": "empty_text"
            }

        print("🔥 embedding texts:", len(texts))

        # =================================
        # EMBEDDINGS

        if not texts:
            return {
                "inserted": 0,
                "status": "empty"
            }
        vectors = embed_texts(texts)

        print("🔥 embeddings done")

        # =================================
        # SAFETY CHECK
        # =================================
        if len(vectors) != len(valid_chunks):

            raise Exception(
                "Vector count mismatch"
            )

        # =================================
        # IDS
        # =================================
        ids = []

        payloads = []

        # =================================
        # BUILD PAYLOADS
        # =================================
        for i, c in enumerate(valid_chunks):

            metadata = c.get("metadata", {})

            ids.append(
                c["id"]
            )

            payloads.append({

                # MAIN CONTENT
                "text":
                    texts[i],

                # SOURCE INFO
                "source":
                    c.get("source", "unknown"),

                "filename":
                    c.get("source", "unknown"),

                "chunk_id":
                    c.get("chunk_id", i),

                # TAGGING
                "language":
                    c.get("language", "text"),

                "topic":
                    c.get("topic", "general"),

                # DUPLICATE DETECTION
                "file_hash":
                    metadata.get("file_hash"),

                # CODE DETECTION
                "is_code":
                    metadata.get("is_code", False)
            })

        print("🔥 qdrant upsert")

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

            "inserted": len(payloads),

            "status": "ok"
        }
