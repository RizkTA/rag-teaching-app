from app.embeddings.embedder import embed_texts
import gc
import psutil

class VectorUpsert:

    def __init__(self, store):

        self.store = store

    def upsert_chunks(self, chunks):

        print("🔥 upsert_chunks start")

        if not chunks:

            return {
                "status": "empty",
                "inserted": 0
            }

        # =====================
        # CLEAN CHUNKS
        # =====================
        valid_chunks = []

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

            valid_chunks.append(c)

        if not valid_chunks:

            return {
                "status": "empty_text",
                "inserted": 0
            }

        print(
            "Valid chunks:",
            len(valid_chunks)
        )

        # =====================
        # BATCH PROCESSING
        # =====================
        BATCH_SIZE = 8

        total_inserted = 0

        total_batches = (
            len(valid_chunks) + BATCH_SIZE - 1
        ) // BATCH_SIZE

        for i in range(
                0,
                len(valid_chunks),
                BATCH_SIZE
        ):

            batch_num = i // BATCH_SIZE + 1

            print(
                f"🔥 Processing batch "
                f"{batch_num}/{total_batches}"
            )

            batch_chunks = valid_chunks[
                i:i + BATCH_SIZE
            ]

            batch_texts = []

            for c in batch_chunks:

                batch_texts.append(
                    str(c["text"]).strip()
                )

            print(
                "Embedding",
                len(batch_texts),
                "texts"
            )
            print(
                "BATCH TEXT CHARS:",
                sum(len(t) for t in batch_texts)
            )
            vectors = embed_texts(
                batch_texts
            )

            if vectors is None:

                raise Exception(
                    "embed_texts returned None"
                )

            if len(vectors) != len(batch_chunks):

                raise Exception(
                    f"Vector mismatch "
                    f"{len(vectors)} vs "
                    f"{len(batch_chunks)}"
                )

            ids = []

            payloads = []

            for j, chunk in enumerate(batch_chunks):

                metadata = chunk.get(
                    "metadata",
                    {}
                )
                print("METADATA =", metadata)
                ids.append(
                    chunk["id"]
                )
                print("DEBUG file_hash =", metadata.get("file_hash"))
                payloads.append({

                    "text":
                        batch_texts[j],

                    "source":
                        chunk.get(
                            "source",
                            "unknown"
                        ),

                    "filename":
                        metadata.get(
                            "filename",
                            chunk.get(
                                "source",
                                "unknown"
                            )
                        ),

                    "chunk_id":
                        chunk.get(
                            "chunk_id",
                            i + j
                        ),

                    "language":
                        chunk.get(
                            "language",
                            "text"
                        ),

                    "topic":
                        chunk.get(
                            "topic",
                            "general"
                        ),

                    "file_hash":
                        metadata.get(
                            "file_hash"
                        ),

                    "is_code":
                        metadata.get(
                            "is_code",
                            False
                        )
                })

            print(
                "Upserting",
                len(ids),
                "vectors"
            )

            self.store.upsert(
                ids,
                vectors,
                payloads
            )

            total_inserted += len(ids)

            print(
                "MEMORY MB:",
                round(
                    psutil.Process()
                    .memory_info()
                    .rss / 1024 / 1024,
                    1
                )
            )

            del vectors
            del ids
            del payloads
            del batch_texts
            del batch_chunks

            gc.collect()

        print("🔥 qdrant complete")

        return {

            "status": "ok",

            "inserted":
                total_inserted
        }