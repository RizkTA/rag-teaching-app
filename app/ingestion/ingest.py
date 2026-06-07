import os
import uuid
import fitz  # PyMuPDF
import re
from pathlib import Path

from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore
from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM


# -----------------------------
# PATH CONFIG
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


# -----------------------------
# INIT QDRANT
# -----------------------------
store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


# -----------------------------
# PDF EXTRACTION
# -----------------------------
def extract_pdf_text(path: str) -> str:
    try:
        doc = fitz.open(path)
        text = ""

        for page in doc:
            text += page.get_text("text") + "\n"

        doc.close()
        return text

    except Exception as e:
        print("❌ PDF extraction failed:", e)
        return ""


# -----------------------------
# SMART CHUNKING (IMPROVED RAG QUALITY)
# -----------------------------
def smart_chunk(text: str, max_size: int = 500, overlap: int = 100):
    """
    Sentence-aware chunking (better than raw slicing)
    """
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?]) +", text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += sentence + " "
        else:
            if current:
                chunks.append(current.strip())

            # overlap handling
            current = sentence[-overlap:] + " " if len(sentence) > overlap else sentence + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# -----------------------------
# DUPLICATE CHECK (FIXED QDRANT FILTER)
# -----------------------------
def is_already_ingested(file_id: str) -> bool:
    try:
        result, _ = store.client.scroll(
            collection_name=store.collection,
            limit=1,
            with_payload=True,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_id",
                        match=MatchValue(value=file_id)
                    )
                ]
            )
        )

        return len(result) > 0

    except Exception as e:
        print("⚠️ Scroll check failed:", e)
        return False


# -----------------------------
# INGEST SINGLE PDF
# -----------------------------
def ingest_pdf(path: str):
    try:
        print(f"\n📄 INGESTING: {path}")

        file_id = os.path.basename(path)

        # skip if already exists
        if is_already_ingested(file_id):
            print(f"⚠️ SKIPPED (already ingested): {file_id}")
            return {"success": True, "skipped": True}

        # extract
        full_text = extract_pdf_text(path)

        if not full_text.strip():
            return {"success": False, "error": "No text extracted"}

        # chunk
        chunks = smart_chunk(full_text)

        # remove tiny noise chunks
        chunks = [c for c in chunks if len(c.strip()) > 50]

        print(f"🧩 CHUNKS CREATED: {len(chunks)}")

        if not chunks:
            return {"success": False, "error": "No valid chunks"}

        # LIMIT SAFETY (avoid API overload)
        chunks = chunks[:2000]

        # embeddings
        vectors = embed_texts(chunks)

        if len(vectors) != len(chunks):
            raise ValueError("❌ Embedding mismatch detected")

        # ids
        ids = [str(uuid.uuid4()) for _ in chunks]

        # payloads
        payloads = [
            {
                "text": chunk,
                "source": file_id,
                "file_id": file_id,
                "chunk_id": i
            }
            for i, chunk in enumerate(chunks)
        ]

        # upsert to qdrant
        store.upsert(ids, vectors, payloads)

        total = store.client.count(
            collection_name=store.collection
        ).count

        print(f"🔥 TOTAL VECTORS IN DB: {total}")

        return {
            "success": True,
            "chunks": len(chunks),
            "total_vectors": total
        }

    except Exception as e:
        print("❌ INGEST FAILED:", e)

        return {
            "success": False,
            "error": str(e)
        }


# -----------------------------
# INGEST ALL PDFs
# -----------------------------
def ingest_all_pdfs(data_folder=DATA_DIR):
    results = []

    print("\n📁 DATA DIR:", data_folder)

    if not os.path.exists(data_folder):
        print("❌ Folder not found")
        return []

    pdf_files = [
        f for f in os.listdir(data_folder)
        if f.lower().endswith(".pdf")
    ]

    print(f"\n📚 FOUND {len(pdf_files)} PDFs")

    for pdf in pdf_files:
        full_path = os.path.join(data_folder, pdf)

        print(f"\n➡️ Processing: {pdf}")

        result = ingest_pdf(full_path)

        results.append({
            "file": pdf,
            "result": result
        })

    print("\n✅ INGEST COMPLETE")

    return results