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
import hashlib

def get_file_hash(path: str):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

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
       # chunks.append(text[start:end])
        chunks.append(str(text[start:end]))
        start += chunk_size - overlap

    return chunks


# ==========================================
# PDF READER
# ==========================================
def read_pdf(path: str):

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:

        try:
            t = page.extract_text()

            if t:
                pages.append(str(t))

        except:
            continue

    # ✅ IMPORTANT: return STRING not list
    return "\n".join(pages)
def clean_text(text: str):

    # 🔥 THIS IS THE FIX LOCATION
    if isinstance(text, list):
        text = " ".join(map(str, text))

    return (
        str(text)
        .replace("â", "-")
        .replace("Â", "")
        .replace("\n", " ")
        .strip()
    )


def is_code_chunk(text: str) -> bool:

    code_indicators = [
        "include <iostream>",
        "int main",
        "cout",
        "printf",
        "def ",
        "function",
        "{",
        "}",
        "print(",
        "return 0"
    ]

    text_lower = text.lower()

    return any(ind.lower() in text_lower for ind in code_indicators)
# ==========================================
# MAIN INGEST (FIXED)
# ==========================================
def ingest_file(path: str, filename: str):

    print("🔥 ingest start:", filename)
    print("🔥 ingest_file called")
    print("🔥 path =", path)
    print("🔥 filename =", filename)
    store = get_store()

    file_hash = get_file_hash(path)

    from qdrant_client.models import (
        Filter,
        FieldCondition,
        MatchValue
    )

    from qdrant_client.models import (
        Filter,
        FieldCondition,
        MatchValue
    )

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
        limit=1,
        with_payload=True
    )

    print("🔥 RECORDS FOUND:", len(records))

    if records:
        return {
            "status": "skipped",
            "message": f"{filename} already exists"
        }
    # DEBUG
    print("🔥 EXISTING:", records)

    print("🔥 RECORDS FOUND:", len(records))

    if len(records) > 0:
        return {
            "status": "skipped",
            "message": f"{filename} already exists"
        }



    suffix = os.path.splitext(filename)[1].lower()

    if suffix == ".pdf":
        text = clean_text(read_pdf(path))

    elif suffix in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    else:
        return {"error": "unsupported file type"}

    try:
        os.remove(path)
    except:
        pass

    if not text or not text.strip():
        return {"error": "empty file"}

    chunks = chunk_text(text)

    structured = []

    for i, chunk in enumerate(chunks):
        structured.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": filename,
            "chunk_id": i,
            "language": "text",
            "topic": "general",

            "metadata": {
                "file_hash": file_hash,

                # optional upgrade
                "is_code": (
                        "include" in chunk or
                        "def " in chunk or
                        "#include" in chunk or
                        "class " in chunk
                )
            }
        })

    upserter = get_upserter()
    result = upserter.upsert_chunks(structured)

    return {
        "filename": filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }