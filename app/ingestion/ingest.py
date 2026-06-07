import os
import uuid
import fitz 
import re

from pathlib import Path

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


# =========================
# PATHS
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

os.makedirs(DATA_DIR, exist_ok=True)


# =========================
# INIT STORE
# =========================
try:

    store = QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

except Exception as e:

    print("❌ Qdrant init failed:", e)

    store = None


# =========================
# PDF EXTRACTION
# =========================
def extract_pdf_text(path):

    try:

        doc = fitz.open(path)

        text = ""

        for page in doc:

            text += page.get_text()

        doc.close()

        return text

    except Exception as e:

        print("❌ PDF extraction failed:", e)

        return ""


# =========================
# CHUNKING
# =========================
def simple_chunk(
    text,
    size=700,
    overlap=150
):

    text = re.sub(r"\s+", " ", text)

    chunks = []

    start = 0

    while start < len(text):

        end = start + size

        chunk = text[start:end]

        if chunk.strip():

            chunks.append(chunk)

        start += size - overlap

    return chunks


# =========================
# INGEST PDF
# =========================
def ingest_pdf(path):

    if store is None:

        return {
            "success": False,
            "error": "Qdrant not initialized"
        }

    try:

        print(f"📄 INGESTING: {path}")

        file_id = os.path.basename(path)

        # =========================
        # EXTRACT
        # =========================
        text = extract_pdf_text(path)

        if not text.strip():

            return {
                "success": False,
                "error": "No text extracted"
            }

        # =========================
        # CHUNK
        # =========================
        chunks = simple_chunk(text)

        chunks = [
            c.strip()
            for c in chunks
            if len(c.strip()) > 50
        ]

        print(
            f"🧩 TOTAL CHUNKS: {len(chunks)}"
        )

        if not chunks:

            return {
                "success": False,
                "error": "No valid chunks"
            }

        # =========================
        # EMBEDDINGS
        # =========================
        vectors = embed_texts(chunks)

        print(
            f"🔥 TOTAL VECTORS: {len(vectors)}"
        )

        # =========================
        # IDS
        # =========================
        ids = [
            str(uuid.uuid4())
            for _ in chunks
        ]

        # =========================
        # PAYLOADS
        # =========================
        payloads = []

        for i, chunk in enumerate(chunks):

            payloads.append({
                "text": chunk,
                "source": file_id,
                "chunk_id": i
            })

        # =========================
        # UPSERT
        # =========================
        store.upsert(
            ids,
            vectors,
            payloads
        )

        # =========================
        # SAFE VECTOR COUNT
        # =========================
        try:

            count = store.client.count(
                collection_name=store.collection
            ).count

        except:

            count = "unknown"

        print(
            f"✅ QDRANT COUNT: {count}"
        )

        return {
            "success": True,
            "chunks": len(chunks),
            "vectors": len(vectors),
            "qdrant_count": count
        }

    except Exception as e:

        print("❌ INGEST FAILED:", e)

        return {
            "success": False,
            "error": str(e)
        }
