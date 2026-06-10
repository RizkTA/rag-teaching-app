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

from app.vectorstores.qdrant_store import QdrantStore
from app.vectorstores.vector_upsert import VectorUpsert


# ==============================
# INIT
# ==============================
store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

upserter = VectorUpsert(store)


# ==============================
# LANGUAGE DETECTION
# ==============================
def detect_language(chunk):

    chunk_lower = chunk.lower()

    cpp_keywords = [
        "#include",
        "cout",
        "cin",
        "std::",
        "int main",
        "using namespace std"
    ]

    python_keywords = [
        "def ",
        "print(",
        "import ",
        "self"
    ]

    cpp_score = sum(k in chunk_lower for k in cpp_keywords)
    py_score = sum(k in chunk_lower for k in python_keywords)

    if cpp_score >= 1:
        return "cpp"

    if py_score >= 1:
        return "python"

    return "text"

# ==============================
# TOPIC DETECTION
# ==============================
def detect_topic(chunk):

    chunk_lower = chunk.lower()

    if "recursion" in chunk_lower:
        return "recursion"

    elif "pointer" in chunk_lower:
        return "pointers"

    elif "array" in chunk_lower:
        return "arrays"

    elif "linked list" in chunk_lower:
        return "linked_lists"

    elif "supervised learning" in chunk_lower:
        return "machine_learning"

    return "general"


# ==============================
# READERS
# ==============================
from pypdf import PdfReader


# ==============================
# SAFE PDF READER
# ==============================
def read_pdf(path: str) -> str:
    """
    Robust PDF text extraction.
    Prevents crashes when extract_text()
    returns None.
    """

    reader = PdfReader(path)

    text = ""

    for page_num, page in enumerate(reader.pages):

        try:

            page_text = page.extract_text()

            # SAFE HANDLING
            text += (page_text or "") + "\n"

        except Exception as e:

            print(
                f"⚠️ Failed reading page {page_num}: {e}"
            )

            continue

    return text



def read_markdown(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_txt(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ==============================
# CHUNKER
# ==============================
# ==============================
# DETECT IF TEXT CONTAINS CODE
# ==============================
def is_code(text):

    text_lower = text.lower()

    patterns = [

        # C++
        "#include",
        "cout <<",
        "cin >>",
        "int main(",
        "std::",

        # Python
        "def ",
        "print(",
        "import ",
        "self.",
        "class ",

        # General code indicators
        "{",
        "}",
        ";",
        "()",
    ]

    for p in patterns:

        if p.lower() in text_lower:
            return True

    return False



import re


def chunk_text(text):

    # -------------------------
    # CODE DETECTION
    # -------------------------
    if is_code(text):

        # split by blank lines
        blocks = re.split(r"\n\s*\n", text)

        chunks = []

        current = ""

        for block in blocks:

            if len(current) + len(block) < 1200:

                current += "\n\n" + block

            else:

                chunks.append(current.strip())

                current = block

        if current:
            chunks.append(current.strip())

        return chunks

    # -------------------------
    # NORMAL TEXT
    # -------------------------
    else:

        chunk_size = 700
        overlap = 100
        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks


# ==============================
# UNIVERSAL INGEST
# ==============================
async def ingest_file(file: UploadFile):

    suffix = os.path.splitext(
        file.filename
    )[1].lower()

    # ==========================
    # SAVE TEMP FILE
    # ==========================
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        tmp.write(await file.read())

        temp_path = tmp.name

    # ==========================
    # EXTRACT TEXT
    # ==========================
    if suffix == ".pdf":

        text = read_pdf(temp_path)

    elif suffix == ".md":

        text = read_markdown(temp_path)

    elif suffix == ".txt":

        text = read_txt(temp_path)

    else:

        os.remove(temp_path)

        return {
            "error": f"Unsupported file type: {suffix}"
        }

    # cleanup
    os.remove(temp_path)

    # ==========================
    # CHUNKING
    # ==========================
    chunks = chunk_text(text)

    # ==========================
    # BUILD STRUCTURED CHUNKS
    # ==========================
    structured = []

    for i, chunk in enumerate(chunks):

        structured.append({

            "id": str(uuid.uuid4()),

            "text": chunk,

            "source": file.filename,

            "chunk_id": i,

            "language": detect_language(chunk),

            "topic": detect_topic(chunk),

            "metadata": {
                "type": suffix.replace(".", "")
            }
        })

    # ==========================
    # UPSERT TO QDRANT
    # ==========================
    result = upserter.upsert_chunks(
        structured
    )

    return {
        "filename": file.filename,
        "chunks": len(structured),
        "status": "ingested",
        "qdrant": result
    }