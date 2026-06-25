import os
import uuid
import hashlib


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
import fitz
import psutil


def read_pdf(path: str) -> str:

    print("📖 START PDF READ")

    doc = fitz.open(path)
    print("PDF PAGES:", len(doc))
    pages = []

    MAX_PAGES = 200

    total_pages = min(
        len(doc),
        MAX_PAGES
    )

    print(
        f"READING {total_pages} PAGES"
    )
    for page_num in range(total_pages):
        page = doc[page_num]

        text = page.get_text("text")

        print(
            f"PAGE {page_num}:",
            len(text)
        )
    for page_num in range(total_pages):

        try:

            page = doc[page_num]

            text = page.get_text("text")

            if text:
                pages.append(text)

        except Exception as e:

            print(
                f"PAGE {page_num} ERROR:",
                e
            )

    doc.close()

    full_text = "\n".join(pages)

    print(
        "TEXT LENGTH:",
        len(full_text)
    )

    print("✅ PDF READ COMPLETE")

    return full_text

# ==========================================
# CHUNKING
# ==========================================
def chunk_text(text):

    if not text:
        return []

    chunk_size = 1200
    overlap = 250

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    print(
        f"🔥 chunked into {len(chunks)} chunks"
    )

    return chunks
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
def ingest_file(
    path: str,
    filename: str,
    replace_existing=True
):
    """
    Ingest a file into Qdrant.

    Features:
    - Deduplication using file hash
    - Optional replacement of existing vectors
    - PDF/TXT/MD support
    - Chunk limiting
    - Validation
    - Detailed logging
    """

    print("=" * 80)
    print("🔥 INGEST START:", filename)
    print("=" * 80)

    try:

        store = get_store()

        file_hash = get_file_hash(path)

        if not file_hash:
            raise Exception("Failed to generate file hash")

        print("FILE HASH:", file_hash)

        # --------------------------------------------------
        # Existing file handling
        # --------------------------------------------------
        print("Generated hash:", file_hash)
        exists = file_exists(store, file_hash)
        print("FILE EXISTS:", exists)
        print("REPLACE EXISTING:", replace_existing)

        print("FILE EXISTS:", exists)

        if exists:

            if replace_existing:

                print("♻ Removing existing vectors")

                store.delete_by_file_hash(file_hash)

                import time
                time.sleep(1)

                print("✅ Old vectors removed")

            else:

                return {
                    "status": "skipped",
                    "message": f"{filename} already exists",
                    "file_hash": file_hash
                }
        # --------------------------------------------------
        # Read file
        # --------------------------------------------------

        suffix = os.path.splitext(filename)[1].lower()

        if suffix == ".pdf":

            print("📄 Reading PDF")
            import psutil

            print(
                "MEMORY MB:",
                round(
                    psutil.Process().memory_info().rss
                    / 1024 / 1024,
                    1
                )
            )
            raw_text = read_pdf(path)
            print(
                "PDF rawww TEXT LENGTH:",
                len(raw_text)
            )
            print("PDF TEXT LENGTH:", len(raw_text))

            if not raw_text.strip():
                print("🔥 NO TEXT FOUND - OCR SHOULD START")
            text = clean_text(raw_text)
            print(
                "PDF TEXT LENGTH:",
                len(text)
            )
            print("UPLOAD SIZE MB:",
                  round(len(raw_text) / 1024 / 1024, 2))

        elif suffix in [".txt", ".md"]:

            print("📄 Reading text file")

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                raw_text = f.read()

            text = clean_text(raw_text)

        else:

            return {
                "status": "error",
                "message": f"Unsupported file type: {suffix}"
            }

        # --------------------------------------------------
        # Validate content
        # --------------------------------------------------

        if not text:

            return {
                "status": "error",
                "message": "File contains no text"
            }

        print("TEXT LENGTH:", len(text))

        # --------------------------------------------------
        # Chunking
        # --------------------------------------------------

        mem("Before chunking")

        chunks = chunk_text(text)
        print("TOTAL CHUNKS:", len(chunks))
        print("TOTAL CHUNKS:", len(chunks))

        if chunks:
            print(
                "AVG CHUNK SIZE:",
                sum(len(c) for c in chunks) / len(chunks)
            )
        mem("After chunking")

        print("TOTAL CHUNKS:", len(chunks))

        MAX_CHUNKS = 25

        if len(chunks) > MAX_CHUNKS:
            print(
                f"⚠ Limiting chunks "
                f"{len(chunks)} -> {MAX_CHUNKS}"
            )

            chunks = chunks[:MAX_CHUNKS]

        if not chunks:

            return {
                "status": "error",
                "message": "No chunks generated"
            }

        # --------------------------------------------------
        # Build chunk objects
        # --------------------------------------------------

        structured = []

        for i, chunk in enumerate(chunks):

            if not chunk:
                continue

            chunk = str(chunk).strip()

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

        print(
            "STRUCTURED CHUNKS:",
            len(structured)
        )

        if not structured:

            return {
                "status": "error",
                "message": "No valid chunks after processing"
            }

        # --------------------------------------------------
        # Upsert
        # --------------------------------------------------

        import time

        mem("Before upsert")

        start = time.time()

        result = get_upserter().upsert_chunks(
            structured
        )

        elapsed = round(
            time.time() - start,
            2
        )

        mem("After upsert")

        print("UPSERT RESULT:", result)
        print("UPSERT TIME:", elapsed, "sec")

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        return {

            "status": "ok",

            "filename": filename,

            "file_hash": file_hash,

            "chunks": len(structured),

            "upsert_time": elapsed,

            "qdrant": result
        }

    except Exception as e:

        print("❌ INGEST ERROR:", str(e))

        import traceback
        traceback.print_exc()

        return {

            "status": "error",

            "message": str(e)
        }