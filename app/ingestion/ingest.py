import os
import uuid
import hashlib
import traceback

from pypdf import PdfReader

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

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
# HASH
# ==========================================
def get_file_hash(path: str) -> str:

    with open(path, "rb") as f:

        return hashlib.md5(
            f.read()
        ).hexdigest()


# ==========================================
# CLEAN TEXT
# ==========================================
def clean_text(text):

    if text is None:
        return ""

    if isinstance(text, list):

        text = " ".join(
            map(str, text)
        )

    return (
        str(text)
        .replace("â", "-")
        .replace("Â", "")
        .replace("\n", " ")
        .strip()
    )


# ==========================================
# PDF
# ==========================================
def read_pdf(path: str) -> str:

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:

        try:

            content = page.extract_text()

            if content:
                pages.append(content)

        except Exception:
            continue

    return "\n".join(pages)


# ==========================================
# CHUNKING
# ==========================================
def chunk_text(text: str):

    text = clean_text(text)

    if not text:
        return []

    text = text[:20000]

    chunk_size = 300
    overlap = 50

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ==========================================
# CODE DETECTION
# ==========================================
def is_code_chunk(text: str) -> bool:

    indicators = [

        "#include",
        "include",
        "cout",
        "printf",
        "def ",
        "class ",
        "return",
        "{",
        "}",
        ";"
    ]

    text_lower = text.lower()

    return any(
        token.lower() in text_lower
        for token in indicators
    )


# ==========================================
# DUPLICATE CHECK
# ==========================================
def file_exists(store, file_hash):

    try:

        records, _ = store.client.scroll(

            collection_name=QDRANT_COLLECTION,

            scroll_filter=Filter(

                must=[

                    FieldCondition(

                        # MATCH YOUR CURRENT PAYLOAD
                        key="file_hash",

                        match=MatchValue(
                            value=file_hash
                        )
                    )
                ]
            ),

            limit=1,

            with_payload=False
        )

        return len(records) > 0

    except Exception as e:

        print("❌ Duplicate check failed:", e)

        return False


# ==========================================
# MAIN INGEST
# ==========================================
def ingest_file(path: str, filename: str):
     print("🔥 ingest start:", filename)
     try:

        print(f"🔥 ingest start: {filename}")

        store = get_store()

        file_hash = get_file_hash(path)

        print("🔥 file hash:", file_hash)

        # ==================================
        # DUPLICATE CHECK
        # ==================================
        if file_exists(store, file_hash):

            return {

                "status": "skipped",

                "message":
                    f"{filename} already exists",

                "file_hash":
                    file_hash
            }

        # ==================================
        # READ FILE
        # ==================================
        suffix = os.path.splitext(
            filename
        )[1].lower()

        if suffix == ".pdf":

            text = clean_text(
                read_pdf(path)
            )

        elif suffix in [".txt", ".md"]:

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = clean_text(
                    f.read()
                )

        else:

            return {

                "status": "error",

                "message":
                    f"Unsupported file type: {suffix}"
            }

        # ==================================
        # EMPTY CHECK
        # ==================================
        if not text:

            return {

                "status": "error",

                "message":
                    "File contains no text"
            }

        # ==================================
        # CHUNK
        # ==================================
        chunks = chunk_text(text)

        if not chunks:

            return {

                "status": "error",

                "message":
                    "No chunks generated"
            }

        structured = []

        for i, chunk in enumerate(chunks):

            structured.append({

                "id":
                    str(uuid.uuid4()),

                "text":
                    chunk,

                "source":
                    filename,

                "chunk_id":
                    i,

                "language":
                    "text",

                "topic":
                    "general",

                "metadata": {

                    "file_hash":
                        file_hash,

                    "filename":
                        filename,

                    "is_code":
                        is_code_chunk(chunk)
                }
            })

        print(
            f"🔥 generated {len(structured)} chunks"
        )

        # ==================================
        # UPSERT
        # ==================================
        result = get_upserter().upsert_chunks(
            structured
        )

        print("🔥 upsert complete")

        return {

            # FRONTEND EXPECTS THIS
            "status": "ok",

            "filename":
                filename,

            "chunks":
                len(structured),

            "file_hash":
                file_hash,

            "qdrant":
                result
        }

    except Exception as e:

        traceback.print_exc()

        return {

            "status": "error",

            "message":
                str(e),

            "traceback":
                traceback.format_exc()
        }

    finally:

        try:

            if os.path.exists(path):
                os.remove(path)

        except Exception:
            pass