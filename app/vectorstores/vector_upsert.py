import uuid
import time
from typing import List, Dict

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


class VectorUpsert:

    def __init__(self, store: QdrantStore):

        self.store = store

        # Number of chunks processed at once
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

        Features:
        - batching
        - rate-limit protection
        - memory-safe
        - Render-safe
        """

        if not chunks:

            return {
                "inserted": 0,
                "status": "empty"
            }

        total_inserted = 0

        # ======================================
        # PROCESS CHUNKS IN BATCHES
        # ======================================
        for start in range(
            0,
            len(chunks),
            self.batch_size
        ):

            end = start + self.batch_size

            chunk_batch = chunks[start:end]

            print(
                f"🚀 Processing batch "
                f"{start} -> {end}"
            )

            # ==================================
            # EXTRACT TEXTS
            # ==================================
            texts = [
                chunk["text"]
                for chunk in chunk_batch
            ]

            # ==================================
            # EMBEDDINGS
            # ==================================
            vectors = embed_texts(texts)

            # Small delay to avoid rate limits
            time.sleep(0.5)

            # ==================================
            # IDS + PAYLOADS
            # ==================================
            ids = []

            payloads = []

            for i, chunk in enumerate(chunk_batch):

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

            total_inserted += len(chunk_batch)

            print(
                f"✅ Inserted "
                f"{len(chunk_batch)} chunks"
            )

        # ======================================
        # FINAL RESULT
        # ======================================
        return {

            "inserted": total_inserted,

            "status": "success"
        }