import os
import uuid
import tempfile

from pypdf import PdfReader
from fastapi import UploadFile

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


# ==============================
# INIT (ONLY ONCE)
# ==============================
store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

upserter = VectorUpsert(store)


# ==============================
# READERS
# ==============================
def read_pdf(path: str) -> str:
    reader = PdfReader(path)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_markdown(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ==============================
# CHUNKING
# ==============================
def chunk_text(text: str, chunk_size=800):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


# ==============================
# UNIVERSAL INGEST (UPLOAD FILE)
# ==============================
async def ingest_file(file: UploadFile):

    suffix = os.path.splitext(file.filename)[1].lower()

    # save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # extract text
    if suffix == ".pdf":
        text = read_pdf(temp_path)

    elif suffix == ".md":
        text = read_markdown(temp_path)

    elif suffix == ".txt":
        text = read_txt(temp_path)

    else:
        os.remove(temp_path)
        return {"error": f"Unsupported file type: {suffix}"}

    os.remove(temp_path)

    # chunk
    chunks = chunk_text(text)

    # build structured chunks
    structured = []
    for i, chunk in enumerate(chunks):

        language = "text"

        if "#include" in chunk:
            language = "cpp"
        elif "def " in chunk:
            language = "python"

        structured.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": file.filename,
            "chunk_id": i,
            "language": language,
            "metadata": {
                "type": suffix.replace(".", "")
            }
        })

    # embed + store (CLEAN WAY)
    result = upserter.upsert_chunks(structured)

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ingested",
        "qdrant": result
    }