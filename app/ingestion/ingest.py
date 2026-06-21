import os
import uuid
import hashlib

print("🔥 INGEST.PY IMPORT START")
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

    print("STORE STEP 1")

    global _store

    if _store is None:

        print("STORE STEP 2")

        _store = QdrantStore(
            QDRANT_URL,
            QDRANT_COLLECTION,
            EMBED_DIM
        )

        print("STORE STEP 3")

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
def chunk_text(text):

    if not text:
        return []

    chunk_size = 1200
    overlap = 250

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    print(
        f"🔥 chunked into {len(chunks)} chunks"
    )

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

from datetime import time
# ==========================================
# MAIN INGEST
# ==========================================
def ingest_file(path: str, filename: str):

    print("🔥 ingest start:", filename)


    try:
        print("BEFORE GET_STORE")
        store = get_store()
        print("AFTER GET_STORE")
        file_hash = get_file_hash(path)

        print("🔥 file hash:", file_hash)
        print("STEP C")
        if file_exists(store, file_hash):

            return {
                "status": "skipped",
                "message": f"{filename} already exists",
                "file_hash": file_hash
            }

        suffix = os.path.splitext(filename)[1].lower()

        if suffix == ".pdf":

            raw_text = read_pdf(path)

            print("RAW TEXT LENGTH:", len(raw_text))
            print(raw_text[:1000])

            text = clean_text(raw_text)

            print("CLEAN TEXT LENGTH:", len(text))
            print("STEP D")
        elif suffix in [".txt", ".md"]:

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                raw_text = read_pdf(path)

                print("RAW LENGTH =", len(raw_text))
                print(raw_text[:1000])

                text = clean_text(raw_text)

                print("CLEAN LENGTH =", len(text))
               # text = clean_text(  f.read())

                print("STEP DD")
        else:

            return {
                "status": "error",
                "message": f"Unsupported file type: {suffix}"
            }

        if not text:

            return {
                "status": "error",
                "message": "File contains no text"
            }


        chunks = chunk_text(text)

        print("TOTAL CHUNKS GENERATED:", len(chunks))
        print(chunks[:10])
        print("STEP E")
        if not chunks:

            return {
                "status": "error",
                "message": "No chunks generated"
            }

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
                    "filename": filename,
                    "is_code": is_code_chunk(chunk)
                }
            })
        print("TOTAL STRUCTURED CHUNKS:", len(structured))
   #     print(f"🔥 generated {len(structured)} chunks")
   #     print("STEP F")
   #     result = get_upserter().upsert_chunks(
#        structured
 #       )
        print(f"🔥 generated {len(structured)} chunks")

        # TEMP TEST
       # structured = structured[:5]

        print(
            f"🔥 TEST MODE: sending {len(structured)} chunks"
        )

        print("STEP F")
        MAX_CHUNKS = 40

        if len(structured) > MAX_CHUNKS:
            print(
                f"⚠️ limiting chunks "
                f"{len(structured)} -> {MAX_CHUNKS}"
            )

            structured = structured[:MAX_CHUNKS]

        t2 = time.time()

        result = get_upserter().upsert_chunks(structured)

        print("UPSERT RESULT:", result)
        print("UPSERT:", time.time() - t2)



       # result = get_upserter().upsert_chunks(

        print("STEP G")
        print("🔥 upsert complete")

        return {
            "status": "ok",
            "filename": filename,
            "chunks": len(structured),
            "file_hash": file_hash,
            "qdrant": result
        }

    except Exception as e:

        print("❌ INGEST ERROR:", str(e))

        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e)
        }



print("🔥 INGEST.PY IMPORT COMPLETE")