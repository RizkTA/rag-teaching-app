import os
import uuid
import tempfile

from fastapi import UploadFile

from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert

# =========================================================
# SINGLETON CACHE (CRITICAL FOR RENDER 512MB)
# =========================================================
from typing import Optional

from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert

_store: Optional[QdrantStore] = None
_upserter: Optional[VectorUpsert] = None

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
# CHUNKING (SAFE + SIMPLE)
# =========================================================
def chunk_text(text: str):

    # handle code blocks first
    if "```" in text:
        return [t.strip() for t in text.split("```") if t.strip()]

    # memory safe limit
    text = text[:40000]

    chunk_size = 350
    overlap = 50

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# =========================================================
# FILE INGEST
# =========================================================
async def ingest_file(file: UploadFile):

    suffix = os.path.splitext(file.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    # -------------------------
    # READ FILE
    # -------------------------
    if suffix == ".pdf":
        from pypdf import PdfReader

        text = "\n".join(
            page.extract_text() or ""
            for page in PdfReader(path).pages
        )

    elif suffix in [".md", ".txt"]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    else:
        os.remove(path)
        return {"error": "unsupported file type"}

    os.remove(path)

    # -------------------------
    # CLEAN TEXT
    # -------------------------
    text = text.strip()

    if not text:
        return {"error": "empty file"}

    # -------------------------
    # CHUNK
    # -------------------------
    print("🔥 chunking")
    chunks = chunk_text(text)

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

    # -------------------------
    # UPSERT (FAST + SAFE)
    # -------------------------
    print("🔥 embedding/upsert")
    upserter = get_upserter()

    print("🔥 embedding/upsert")

    result = upserter.upsert_chunks(structured)

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }