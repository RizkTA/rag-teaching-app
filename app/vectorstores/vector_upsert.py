import uuid
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):

        self.store = store

        # ==========================
        # EMBEDDING BATCH SIZE
        # ==========================
        self.batch_size = 32

    # ==========================================
    # MAIN UPSERT FUNCTION
    # ==========================================
    def upsert_chunks(
        self,
        chunks: List[Dict]
    ):
        """
        Convert chunks → embeddings → Qdrant

        Uses batching to avoid:
        - RAM crashes
        - Render timeouts
        - embedding overload
        """

        if not chunks:

            return {
                "inserted": 0,
                "status": "empty"
            }

        total_inserted = 0

        # ======================================
        # PROCESS IN BATCHES
        # ======================================
        for start in range(
            0,
            len(chunks),
            self.batch_size
        ):

            end = start + self.batch_size

            batch = chunks[start:end]

            print(
                f"🚀 Processing batch "
                f"{start} → {end}"
            )

            # ==================================
            # EXTRACT TEXTS
            # ==================================
            texts = [
                c["text"]
                for c in batch
            ]

            # ==================================
            # EMBEDDINGS
            # ==================================
            vectors = embed_texts(texts)

            ids = []

            payloads = []

            # ==================================
            # BUILD PAYLOADS
            # ==================================
            for i, chunk in enumerate(batch):

                ids.append(
                    chunk.get(
                        "id",
                        str(uuid.uuid4())
                    )
                )

                payloads.append({

                    "text": chunk["text"],

                    "source": chunk.get(
                        "source",
                        "unknown"
                    ),

                    "chunk_id": chunk.get(
                        "chunk_id",
                        i
                    ),

                    "language": chunk.get(
                        "language",
                        "text"
                    ),

                    "topic": chunk.get(
                        "topic",
                        "general"
                    ),

                    "metadata": chunk.get(
                        "metadata",
                        {}
                    )
                })

            # ==================================
            # UPSERT TO QDRANT
            # ==================================
            self.store.upsert(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )

            total_inserted += len(batch)

            print(
                f"✅ Inserted batch "
                f"({len(batch)} chunks)"
            )

        # ======================================
        # FINAL RESULT
        # ======================================
        return {

            "inserted": total_inserted,

            "status": "success"
        }