import os
import uuid
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
        _upserter = VectorUpsert(get_store())

    return _upserter


# ==========================================
# CHUNKING (SAFE)
# ==========================================
def chunk_text(text: str):

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
# PDF READER
# ==========================================
def read_pdf(path: str):

    reader = PdfReader(path)

    text = []

    for page in reader.pages:

        try:
            t = page.extract_text()
            if t:
                text.append(t)
        except:
            continue

    def clean_text(text: str):
        return (
            text.encode("utf-8", errors="ignore")
            .decode("utf-8", errors="ignore")
            .replace("â", "-")
            .replace("Â", "")
            .replace("\n", " ")
            .strip()
        )

    text = clean_text(text)
    return "\n".join(text)


# ==========================================
# MAIN INGEST (FIXED)
# ==========================================
def ingest_file(path: str, filename: str):

    print("🔥 ingest start:", filename)

    suffix = os.path.splitext(filename)[1].lower()

    # =========================
    # READ FILE
    # =========================
    if suffix == ".pdf":
        text = read_pdf(path)

    elif suffix in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    else:
        return {"error": "unsupported file type"}

    # cleanup
    try:
        os.remove(path)
    except:
        pass

    if not text or not text.strip():
        return {"error": "empty file"}

    # =========================
    # CHUNK
    # =========================
    chunks = chunk_text(text)

    print("🔥 chunks:", len(chunks))

    structured = []

    for i, chunk in enumerate(chunks):

        structured.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": filename,
            "chunk_id": i,
            "language": "text",
            "topic": "general",
            "metadata": {}
        })

    # =========================
    # UPSERT
    # =========================
    upserter = get_upserter()

    result = upserter.upsert_chunks(structured)

    print("🔥 upsert done")

    return {
        "filename": filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }