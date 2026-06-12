import os
import uuid
import tempfile
import gc

from fastapi import UploadFile

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


# =========================================================
# SINGLETON CACHE
# =========================================================
_store = None
_upserter = None


def get_store():
    global _store

    if _store is None:

        _store = QdrantStore(
            QDRANT_URL,
            QDRANT_COLLECTION,
            EMBED_DIM
        )

    return _store


def get_upserter():
    global _upserter

    if _upserter is None:

        _upserter = VectorUpsert(
            get_store()
        )

    return _upserter


# =========================================================
# CHUNKING
# =========================================================
def chunk_text(text: str):

    # CODE BLOCK PRESERVATION
    if "```" in text:

        chunks = [
            t.strip()
            for t in text.split("```")
            if t.strip()
        ]

        return chunks[:40]

    # MEMORY LIMIT
    text = text[:30000]

    chunk_size = 300
    overlap = 40

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - overlap

    return chunks[:60]


# =========================================================
# SAFE PDF READER
# =========================================================
def read_pdf(path):

    from pypdf import PdfReader

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:

        try:

            txt = page.extract_text()

            if txt:
                pages.append(txt)

        except:
            continue

    return "\n".join(pages)


# =========================================================
# INGEST FILE
# =========================================================
async def ingest_file(file: UploadFile):

    if not file.filename:
        return {"error": "missing filename"}

    suffix = os.path.splitext(
        file.filename
    )[1].lower()

    # =====================================================
    # SAVE TEMP FILE
    # =====================================================
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        content = await file.read()

        tmp.write(content)

        path = tmp.name

    # FREE MEMORY IMMEDIATELY
    del content
    gc.collect()

    # =====================================================
    # READ FILE
    # =====================================================
    try:

        if suffix == ".pdf":

            text = read_pdf(path)

        elif suffix in [".txt", ".md"]:

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = f.read()

        else:

            os.remove(path)

            return {
                "error": "unsupported file type"
            }

    except Exception as e:

        os.remove(path)

        return {
            "error": f"read error: {str(e)}"
        }

    # CLEANUP TEMP FILE
    os.remove(path)

    # =====================================================
    # CLEAN TEXT
    # =====================================================
    text = text.strip()

    if not text:

        return {
            "error": "empty file"
        }

    # =====================================================
    # CHUNK
    # =====================================================
    print("🔥 chunking")

    chunks = chunk_text(text)

    # FREE MEMORY
    del text
    gc.collect()

    # =====================================================
    # STRUCTURE CHUNKS
    # =====================================================
    structured = []

    for i, chunk in enumerate(chunks):

        structured.append({

            "id": str(uuid.uuid4()),

            "text": chunk,

            "source": file.filename,

            "chunk_id": i,

            "language": "text",

            "topic": "general",

            "metadata": {}
        })

    # =====================================================
    # UPSERT
    # =====================================================
    print("🔥 embedding/upsert")

    upserter = get_upserter()

    result = upserter.upsert_chunks(
        structured
    )

    # FINAL CLEANUP
    del structured
    del chunks

    gc.collect()

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "status": "ok",
        "qdrant": result
    }