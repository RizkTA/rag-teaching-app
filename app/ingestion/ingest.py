import os
import uuid
import hashlib

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
# FILE HASH
# ==========================================
def get_file_hash(path: str):

    with open(path, "rb") as f:

        return hashlib.md5(
            f.read()
        ).hexdigest()


# ==========================================
# CLEAN TEXT
# ==========================================
def clean_text(text):

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

    return "\n".join(pages)


# ==========================================
# CHUNKING
# ==========================================
def chunk_text(text: str):

    text = text[:20000]

    chunk_size = 300
    overlap = 50

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            str(text[start:end])
        )

        start += chunk_size - overlap

    return chunks


# ==========================================
# CODE DETECTION
# ==========================================
def is_code_chunk(text: str):

    indicators = [

        "include",

        "#include",

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
        k.lower() in text_lower
        for k in indicators
    )


# ==========================================
# MAIN INGEST
# ==========================================
def ingest_file(path: str, filename: str):

    print("🔥 ingest start:", filename)

    store = get_store()

    # =====================================
    # FILE HASH
    # =====================================
    file_hash = get_file_hash(path)

    print("🔥 FILE HASH:", file_hash)

    # =====================================
    # DUPLICATE CHECK
    # IMPORTANT:
    # MUST MATCH YOUR PAYLOAD STRUCTURE
    # metadata.file_hash
    # =====================================
    try:

        records, _ = store.client.scroll(

            collection_name=QDRANT_COLLECTION,

            scroll_filter=Filter(

                must=[

                    FieldCondition(

                        key="metadata.file_hash",

                        match=MatchValue(
                            value=file_hash
                        )
                    )
                ]
            ),

            limit=1,

            with_payload=True
        )

        print("🔥 RECORDS FOUND:", len(records))

        # =================================
        # FILE ALREADY EXISTS
        # =================================
        if len(records) > 0:

            return {

                "status": "skipped",

                "message":
                    f"{filename} already exists",

                "file_hash":
                    file_hash
            }

    except Exception as e:

        print("❌ DUPLICATE CHECK ERROR:", e)

    # =====================================
    # READ FILE
    # =====================================
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
            encoding="utf-8"
        ) as f:

            text = clean_text(
                f.read()
            )

    else:

        return {
            "status": "error",
            "message": "unsupported file type"
        }

    # =====================================
    # CLEANUP TEMP FILE
    # =====================================
    try:
        os.remove(path)
    except:
        pass

    # =====================================
    # EMPTY FILE CHECK
    # =====================================
    if not text or not text.strip():

        return {
            "status": "error",
            "message": "empty file"
        }

    # =====================================
    # CHUNKING
    # =====================================
    chunks = chunk_text(text)

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

                # IMPORTANT
                "file_hash":
                    file_hash,

                "filename":
                    filename,

                "is_code":
                    is_code_chunk(chunk)
            }
        })

    print("🔥 CHUNKS:", len(structured))

    # =====================================
    # UPSERT
    # =====================================
    upserter = get_upserter()

    result = upserter.upsert_chunks(
        structured
    )

    print("🔥 UPSERT COMPLETE")

    return {

        "status": "uploaded",

        "filename":
            filename,

        "chunks":
            len(structured),

        "file_hash":
            file_hash,

        "qdrant":
            result
    }