import os
import uuid
import tempfile

from fastapi import UploadFile

from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


_store = None
_upserter = None


def get_store():
    global _store
    if _store is None:
        _store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)
    return _store


def get_upserter():
    global _upserter
    if _upserter is None:
        _upserter = VectorUpsert(get_store())
    return _upserter


def chunk_text(text):

    if "```" in text:
        return text.split("```")

    chunk_size = 500
    overlap = 100

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


async def ingest_file(file: UploadFile):

    suffix = os.path.splitext(file.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    if suffix == ".pdf":
        from pypdf import PdfReader
        text = "\n".join(
            page.extract_text() or ""
            for page in PdfReader(path).pages
        )
    else:
        text = open(path, "r", encoding="utf-8").read()

    os.remove(path)

    text = text[:150000]

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

    upserter = get_upserter()

    result = upserter.upsert_chunks(structured)

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }