import os
import uuid
import tempfile
import re

from fastapi import UploadFile
from pypdf import PdfReader

from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


# ==========================
# SAFE INIT (LAZY)
# ==========================
def get_store():
    return QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )


def get_upserter():
    return VectorUpsert(get_store())

def chunk_text(text):

 if "```" in text:
    return text.split("```")



# ==========================
# DETECT CODE
# ==========================
def is_code(text):

    text_lower = text.lower()

    patterns = [
        "#include", "cout", "cin", "int main", "std::",
        "def ", "print(", "import ", "self", "class ",
        "{", "}", ";"
    ]

    return any(p in text_lower for p in patterns)


# ==========================
# LANGUAGE DETECTION
# ==========================
def detect_language(text):

    if any(k in text.lower() for k in ["#include", "cout", "cin"]):
        return "cpp"

    if any(k in text.lower() for k in ["def ", "import ", "print("]):
        return "python"

    return "text"


# ==========================
# TOPIC DETECTION
# ==========================
def detect_topic(text):

    t = text.lower()

    if "recursion" in t:
        return "recursion"
    if "array" in t:
        return "arrays"
    if "pointer" in t:
        return "pointers"

    return "general"


# ==========================
# SAFE PDF READER (PAGE LEVEL)
# ==========================
def read_pdf(path):

    from pypdf import PdfReader

    reader = PdfReader(path)

    text = []

    for page in reader.pages:

        try:
            t = page.extract_text()
            if t:
                text.append(t)

        except:
            continue

    return "\n".join(text)

# ==========================
# CHUNKING
# ==========================
def chunk_text(text):

    # 🔥 REMOVE BIG TEXT CRASHES
    if len(text) > 50_000:
        text = text[:50_000]

    # simple safe chunking
    chunk_size = 500
    overlap = 100

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size
        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks

# ==========================
# INGEST FILE
# ==========================
async def ingest_file(file: UploadFile):

    suffix = os.path.splitext(file.filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    if suffix == ".pdf":
        text = read_pdf(path)
    elif suffix == ".md":
        text = open(path, "r", encoding="utf-8").read()
    elif suffix == ".txt":
        text = open(path, "r", encoding="utf-8").read()
    else:
        os.remove(path)
        return {"error": "unsupported file"}

    os.remove(path)

    # 🔥 safety cap (IMPORTANT for Render)
    text = text[:150000]

    chunks = chunk_text(text)

    structured = []

    for i, chunk in enumerate(chunks):

        structured.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": file.filename,
            "chunk_id": i,
            "language": detect_language(chunk),
            "topic": detect_topic(chunk),
            "metadata": {"type": suffix.replace(".", "")}
        })

    upserter = None

    def get_upserter():
        global upserter
        if upserter is None:
            upserter = VectorUpsert()
        return upserter

    result = upserter.upsert_chunks(structured)

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ok",
        "qdrant": result
    }