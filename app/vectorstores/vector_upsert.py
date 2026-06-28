from app.embeddings.embedder import embed_texts
from app.utils.progress import update_job

import gc
import psutil
import ctypes


class VectorUpsert:

    def __init__(self, store):
        self.store = store

    def upsert_chunks(
        self,
        chunks,
        job_id=None
    ):
        print("=" * 80)
        print("🔥 UPSERT START")
        print("=" * 80)

        if not chunks:
            return {
                "status": "empty",
                "inserted": 0
            }

        # ---------------------------------------
        # Validate chunks
        # ---------------------------------------

        valid_chunks = []

        for chunk in chunks:

            text = chunk.get("text")

            if text is None:
                continue

            text = str(text).strip()

            if not text:
                continue

            chunk["text"] = text

            valid_chunks.append(chunk)

        if not valid_chunks:
            return {
                "status": "empty_text",
                "inserted": 0
            }

        print(
            "Valid chunks:",
            len(valid_chunks)
        )

        EMBED_BATCH = 8

        inserted = 0

        total_batches = (
                                len(valid_chunks)
                                + EMBED_BATCH
                                - 1
                        ) // EMBED_BATCH

        for batch_index in range(
                0,
                len(valid_chunks),
                EMBED_BATCH
        ):

            batch_number = batch_index // EMBED_BATCH + 1

            batch = valid_chunks[
                batch_index:
                batch_index + EMBED_BATCH
            ]

            if job_id:
                progress = 55 + int(
                    batch_number / total_batches * 40
                )

                update_job(

                    job_id,

                    progress=progress,

                    stage=f"Embedding batch {batch_number}/{total_batches}"

                )

            print(
                f"\nBatch {batch_number}/{total_batches}"
            )

            texts = [
                c["text"]
                for c in batch
            ]

            vectors = embed_texts(texts)

            if vectors is None:
                raise RuntimeError(
                    "Embedding failed."
                )

            ids = []

            payloads = []

            for vector, chunk in zip(
                    vectors,
                    batch
            ):
                metadata = chunk.get(
                    "metadata",
                    {}
                )

                ids.append(
                    chunk["id"]
                )

                payloads.append({

                    "text":
                        chunk["text"],

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
                            0
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

                    "page":
                        metadata.get(
                            "page"
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
                "Uploading",
                len(ids),
                "vectors"
            )

            self.store.upsert(
                ids,
                vectors,
                payloads
            )

            inserted += len(ids)

            print(
                "Memory:",
                round(
                    psutil.Process().memory_info().rss
                    / 1024 / 1024,
                    1
                ),
                "MB"
            )

            # --------------------------
            # Free everything
            # --------------------------

            del texts
            del vectors
            del ids
            del payloads
            del batch

            gc.collect()

            try:
                ctypes.CDLL(
                    "libc.so.6"
                ).malloc_trim(0)
            except Exception:
                pass

        del valid_chunks

        gc.collect()

        try:
            ctypes.CDLL(
                "libc.so.6"
            ).malloc_trim(0)
        except Exception:
            pass
        if job_id:
            update_job(

                job_id,

                progress=98,

                stage="Saving vectors..."

            )
        print("=" * 80)
        print("✅ UPSERT COMPLETE")
        print("=" * 80)
        if job_id:
            update_job(

                job_id,

                progress=100,

                stage="Completed"

            )
        try:
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except Exception:
            pass
        return {

            "status": "ok",

            "inserted": inserted

        }