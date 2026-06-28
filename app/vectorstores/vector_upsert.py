from app.embeddings.embedder import embed_texts
from app.jobs import get_job, list_jobs, update_job, create_job, finish_job,delete_job

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

        # --------------------------------------------------
        # Validate chunks
        # --------------------------------------------------

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

        print("Valid chunks:", len(valid_chunks))

        EMBED_BATCH = 8

        inserted = 0

        total_batches = (
            len(valid_chunks)
            + EMBED_BATCH
            - 1
        ) // EMBED_BATCH

        # --------------------------------------------------
        # Process batches
        # --------------------------------------------------

        for batch_index in range(
            0,
            len(valid_chunks),
            EMBED_BATCH
        ):

            batch_number = (
                batch_index // EMBED_BATCH
            ) + 1

            batch = valid_chunks[
                batch_index:
                batch_index + EMBED_BATCH
            ]

            if job_id:

                progress = min(
                    95,
                    55 + int(
                        batch_number * 40 / total_batches
                    )
                )

                update_job(
                    job_id,
                    progress=progress,
                    stage=f"🧠 Embedding batch {batch_number}/{total_batches}"
                )

            print(
                f"\n🔥 Batch {batch_number}/{total_batches}"
            )

            texts = None
            vectors = None
            ids = None
            payloads = None

            try:

                texts = [
                    c["text"]
                    for c in batch
                ]

                vectors = embed_texts(texts)

                if not vectors:
                    raise RuntimeError(
                        "Embedding failed."
                    )

                if len(vectors) != len(texts):

                    raise RuntimeError(

                        f"Embedding count mismatch "

                        f"{len(vectors)} != {len(texts)}"

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

                        psutil.Process()

                        .memory_info()

                        .rss

                        / 1024 / 1024,

                        1

                    ),

                    "MB"

                )

            finally:

                try:
                    del metadata
                except:
                    pass

                try:
                    del texts
                except:
                    pass

                try:
                    del vectors
                except:
                    pass

                try:
                    del ids
                except:
                    pass

                try:
                    del payloads
                except:
                    pass

                try:
                    del batch
                except:
                    pass

                gc.collect()

                try:

                    ctypes.CDLL(
                        "libc.so.6"
                    ).malloc_trim(0)

                except Exception:

                    pass

        # --------------------------------------------------
        # Final cleanup
        # --------------------------------------------------

        try:
            del valid_chunks
        except:
            pass

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

                stage="💾 Saving vectors..."

            )

        print("=" * 80)
        print("✅ UPSERT COMPLETE")
        print("=" * 80)

        return {

            "status": "ok",

            "inserted": inserted

        }