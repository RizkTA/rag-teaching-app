import os
import uuid
import hashlib
from app.ingestion.chunker import (
    chunk_text,
    stream_chunks
)
from .pdf_stream import stream_pdf_pages
print("🔥 INGEST.PY IMPORT START")
from pypdf import PdfReader

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)
from app.jobs import update_job
from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert
import psutil

def mem(label):
    print(
        label,
        psutil.Process().memory_info().rss / 1024 / 1024,
        "MB"
    )
# ==========================================
# SINGLETONS
# ==========================================
_store = None
_upserter = None

def get_store():

    print("STORE STEP 1")

    global _store

    if _store is None:

        print("STORE STEP 2")

        _store = QdrantStore(
            QDRANT_URL,
            QDRANT_COLLECTION,
            EMBED_DIM
        )

        print("STORE STEP 3")

    return _store


def get_upserter():
    global _upserter

    if _upserter is None:
        _upserter = VectorUpsert(
            get_store()
        )

    return _upserter


# ==========================================
# HASH
# ==========================================
import hashlib

def get_file_hash(path: str) -> str:
    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()

# ==========================================
# CLEAN TEXT
# ==========================================
def clean_text(text):
    if text is None:
        return ""

    if isinstance(text, list):
        text = " ".join(
            map(str, text)
        )

    return (
        str(text)
        .replace("â", "-")
        .replace("Â", "")
        .replace("\n", " ")
        .strip()
    )


# ==========================================
# PDF
# ==========================================

import psutil


import gc

import pytesseract
from PIL import Image

import gc

import fitz
import pytesseract

from PIL import Image



# ==========================================
# CHUNKING
# ==========================================

# ==========================================
# CODE DETECTION
# ==========================================
def is_code_chunk(text: str) -> bool:
    indicators = [

        "#include",
        "include",
        "cout",
        "printf",
        "def ",
        "class ",
        "return",
        "{",
        "}",
        ";"
    ]

    text_lower = text.lower()

    return any(
        token.lower() in text_lower
        for token in indicators
    )


# ==========================================
# DUPLICATE CHECK
# ==========================================
def file_exists(store, file_hash):

    try:

        records, _ = store.client.scroll(

            collection_name=QDRANT_COLLECTION,

            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_hash",
                        match=MatchValue(value=file_hash)
                    )
                ]
            ),

            limit=5,
            with_payload=True
        )

        print("HASH LOOKUP:", file_hash)
        print("MATCHES FOUND:", len(records))

        for r in records:
            print("MATCH PAYLOAD:", r.payload)

        return len(records) > 0

    except Exception as e:

        print("❌ Duplicate check failed:", e)

        return False
from datetime import time
# ==========================================
# MAIN INGEST
# ==========================================
from app.jobs import update_job
def ingest_file(
    path: str,
    filename: str,
    replace_existing=True,
    job_id=None
):

    print("=" * 80)
    print("🔥 INGEST START:", filename)
    print("=" * 80)
    if job_id:
        update_job(
            job_id,
            progress=1,
            stage="Initializing upload..."
        )
    try:

        store = get_store()

        file_hash = get_file_hash(path)
        if job_id:
            update_job(
                job_id,
                progress=5,
                stage="Checking for duplicates..."
            )
        if not file_hash:
            raise Exception("Failed to generate file hash")

        print("FILE HASH:", file_hash)

        # --------------------------------------------------
        # Duplicate handling
        # --------------------------------------------------

        exists = file_exists(store, file_hash)

        print("FILE EXISTS:", exists)
        print("REPLACE EXISTING:", replace_existing)

        if exists:

            if replace_existing:
                if job_id:
                    update_job(
                        job_id,
                        progress=8,
                        stage="Removing previous version..."
                    )
                print("♻ Removing existing vectors")

                store.delete_by_file_hash(file_hash)

                import time
                time.sleep(1)

            else:

                return {

                    "status": "skipped",

                    "message": f"{filename} already exists",

                    "file_hash": file_hash

                }

        suffix = os.path.splitext(filename)[1].lower()

        total_chunks = 0

        # ==================================================
        # PDF
        # ==================================================

        if suffix == ".pdf":
            if job_id:
                update_job(
                    job_id,
                    progress=10,
                    stage="Reading PDF..."
                )
            print("📄 Streaming PDF")

            chunk_id = 0

            for page_num, page_text in enumerate(
                    stream_pdf_pages(path),
                    start=1
            ):
                if job_id:
                    progress = min(
                        10 + page_num * 2,
                        40
                    )

                    update_job(

                        job_id,

                        progress=progress,

                        stage=f"Processing page {page_num}"

                    )
                print("=" * 60)
                print(f"PAGE {page_num}")
                print("=" * 60)

                page_text = clean_text(page_text)

                if not page_text:
                    print("Empty page")
                    continue
                if job_id:
                    progress = min(
                        10 + page_num * 2,
                        40
                    )
                structured = []
                estimated_chunks = 0

                for chunk in stream_chunks(
                        page_text,
                        job_id=job_id
                ):

                    estimated_chunks += 1

                    if job_id:
                        update_job(
                            job_id,
                            stage=f"Embedding page {page_num}",
                            chunks=chunk_id,
                            progress=min(80, 55 + estimated_chunks)
                        )


                    if not chunk:
                        continue

                    structured.append({

                        "id": str(uuid.uuid4()),

                        "text": chunk,

                        "source": filename,

                        "chunk_id": chunk_id,

                        "language": "text",

                        "topic": "general",

                        "metadata": {

                            "file_hash": file_hash,

                            "filename": filename,

                            "page": page_num,

                            "is_code": is_code_chunk(chunk)

                        }

                    })

                    chunk_id += 1

                if structured:

                    print(
                        f"Uploading {len(structured)} chunks"
                    )
                    if job_id:
                        update_job(

                            job_id,

                            progress=55,

                            stage=f"Embedding page {page_num}"

                        )

                    get_upserter().upsert_chunks(

                        structured,

                        job_id=job_id

                    )


                    total_chunks += len(structured)

                # -------------------------
                # FREE MEMORY
                # -------------------------

                del structured

                del page_text

                import gc
                gc.collect()

                try:
                    import ctypes
                    ctypes.CDLL(
                        "libc.so.6"
                    ).malloc_trim(0)
                except Exception:
                    pass
                if page_num % 10 == 0:
                    mem(f"After page {page_num}")

        # ==================================================
        # TXT / MD
        # ==================================================

        elif suffix in [".txt", ".md"]:

            with open(
                    path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
            ) as f:

                text = clean_text(f.read())

            chunks = chunk_text(
                text,
                job_id=job_id
            )

            structured = []

            for i, chunk in enumerate(chunks):

                chunk = chunk.strip()

                if not chunk:
                    continue

                structured.append({

                    "id": str(uuid.uuid4()),

                    "text": chunk,

                    "source": filename,

                    "chunk_id": i,

                    "language": "text",

                    "topic": "general",

                    "metadata": {

                        "file_hash": file_hash,

                        "filename": filename,

                        "is_code": is_code_chunk(chunk)

                    }

                })

            if not structured:

                return {

                    "status": "error",

                    "message": "No valid chunks generated"

                }


            get_upserter().upsert_chunks(
                structured,
                job_id=job_id
            )
            total_chunks = len(structured)

        else:

            return {

                "status": "error",

                "message": f"Unsupported file type: {suffix}"

            }

        print("=" * 80)
        print("INGEST COMPLETE")
        print("TOTAL CHUNKS:", total_chunks)
        print("=" * 80)
        if job_id:
            update_job(

                job_id,

                progress=100,

                stage="Completed"

            )
        return {

            "status": "ok",

            "filename": filename,

            "file_hash": file_hash,

            "chunks": total_chunks

        }

    except Exception as e:

        print("❌ INGEST ERROR:", str(e))

        import traceback
        traceback.print_exc()
        if job_id:
            update_job(

                job_id,

                progress=100,

                stage=f"Failed: {e}"

            )
        return {

            "status": "error",

            "message": str(e)

        }