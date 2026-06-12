import os
import uuid
import tempfile

from fastapi import UploadFile
from pypdf import PdfReader

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


# ==========================================
# SINGLETONS
# ==========================================
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


# ==========================================
# SAFE CHUNKING
# ==========================================
def chunk_text(text):

    text = text[:20000]

    chunk_size = 300
    overlap = 50

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks


# ==========================================
# SAFE PDF READER
# ==========================================
def read_pdf(path):

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


# ==========================================
# INGEST
# ==========================================
async def ingest_file(file: UploadFile):

    print("🔥 ingest start")

    suffix = os.path.splitext(
        file.filename
    )[1].lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        content = await file.read()

        tmp.write(content)

        path = tmp.name

    print("🔥 temp file saved")

    # ======================================
    # READ FILE
    # ======================================
    if suffix == ".pdf":

        text = read_pdf(path)

    elif suffix in [".txt", ".md"]:

        with open(path, "r", encoding="utf-8") as f:

            text = f.read()

    else:

        os.remove(path)

        return {
            "error": "unsupported file"
        }

    os.remove(path)

    print("🔥 file parsed")

    if not text.strip():

        return {
            "error": "empty text"
        }

    # ======================================
    # CHUNK
    # ======================================
    chunks = chunk_text(text)

    print("🔥 chunks:", len(chunks))

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

    # ======================================
    # UPSERT
    # ======================================
    upserter = get_upserter()

    result = upserter.upsert_chunks(
        structured
    )

    print("🔥 upsert done")

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }