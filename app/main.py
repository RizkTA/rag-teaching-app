import uuid

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import psutil
import os
print(
    "MEMORY MB:",
    psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
)
print("🔥 BEFORE INGEST IMPORT")
import os
import pandas as pd
from datetime import datetime

HISTORY_CSV = "data/file_history.csv"

def save_history(filename, chunks, file_hash):
    row = {
        "filename": filename,
        "chunks": chunks,
        "file_hash": file_hash,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(HISTORY_CSV):
        df = pd.read_csv(HISTORY_CSV)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv(HISTORY_CSV, index=False)
    print("Saving to:", os.path.abspath(UPLOAD_HISTORY_FILE))
    print("✅ HISTORY SAVED")
#from app.ingestion.ingest import ingest_file

print("🔥 AFTER INGEST IMPORT")
print("🔥 MAIN.PY LOADED")

from app.rag.fusion_rag import fusion_search
from app.llm.streaming import stream_answer
try:
    import multipart

    print("🔥 MULTIPART OK")
    print("🔥 VERSION:", multipart.__version__)

except Exception as e:
    print("❌ MULTIPART FAILED")
    print(e)
# =====================================
# FASTAPI
# =====================================
app = FastAPI()
from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType

def create_qdrant_indexes():
    import os
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    try:
        client.create_payload_index(
            collection_name=QDRANT_COLLECTION,
            field_name="file_hash",
            field_schema=PayloadSchemaType.KEYWORD
        )

        print("✅ file_hash index created")

    except Exception as e:
        print("Index creation skipped:", e)
@app.on_event("startup")
async def startup_event():
    create_qdrant_indexes()
@app.get("/qdrant_count")
def qdrant_count():

    store = get_store()

    count = store.client.count(
        collection_name=store.collection_name
    )

    return count
from app.embeddings.embedder import get_embedder

@app.on_event("startup")
async def startup_event():
    print("🔥 Preloading embedder...")
    get_embedder()
    print("🔥 Embedder ready")
@app.get("/versions")
def versions():
    import numpy
    import torch
    import transformers
    import sentence_transformers
    import huggingface_hub

    return {
        "numpy": numpy.__version__,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "sentence_transformers": sentence_transformers.__version__,
        "huggingface_hub": huggingface_hub.__version__,
    }
from fastapi import Request
@app.get("/")
def root():

    import psutil
    import os

    print(
        "MEMORY MB:",
        psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    )

    return {"status":"ok"}
@app.middleware("http")
async def log_every_request(request: Request, call_next):

    print(
        "🔥 REQUEST:",
        request.method,
        request.url.path
    )

    response = await call_next(request)

    print(
        "🔥 RESPONSE:",
        response.status_code
    )

    return response

# =====================================
# MODELS
# =====================================
class QueryRequest(BaseModel):
    q: str


# =====================================
# ROOT
# =====================================
@app.get("/")
def root():
    return {"status": "ok"}


@app.head("/")
def root_head():
    return


# =====================================
# HEALTH
# =====================================
@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================
# TEST
# =====================================
@app.get("/test")
def test():

    print("🔥 TEST ENDPOINT HIT")

    return {
        "status": "test_ok"
    }


# =====================================
# UPLOAD TEST
# =====================================
@app.get("/upload_test")
async def upload_test():

    print("🔥 upload_test reached")

    return {
        "message": "upload route server alive"
    }


# =====================================
# QUERY
# =====================================
@app.post("/query")
def query(req: QueryRequest):

    try:

        results = fusion_search(req.q)
        print("\n========== RETRIEVED RESULTS ==========")
        if not results:
            print("RETURNING I DONT KNOW")

            return {
                "answer": "I don't know based on the documents.",
                "sources": []
            }
        for r in results:
            print(
                f"SCORE={r['final_score']:.3f}",
                r["source"]
            )

            print(r["text"][:250])

            print("--------------------------------")
        if not results:
            return {
                "answer": "I don't know based on the documents.",
                "sources": []
            }

        context = "\n\n".join(
            [r["text"] for r in results]
        )[:2500]

        print("\n========== CONTEXT ==========")
        print(context[:2000])
        print("=============================\n")
        prompt = f"""
        You are a helpful teaching assistant.

        Answer ONLY using the provided context.

        If the answer is not contained in the context,
        respond exactly:

        I don't know based on the documents.

        Rules:
        - Use the context only
        - Give a detailed explanation
        - Use examples when available
        - Include code if relevant

        Context:
        {context}

        Question:
        {req.q}

        Answer:
        """
        #print("========== CONTEXT ==========")
        print("========== CONTEXT ==========")

        for r in results:
            print(r["source"])
            print(r["text"][:500])
            print("----------------")

            print()
        answer_parts = []

        for chunk in stream_answer(prompt):

            if isinstance(chunk, dict):

                answer_parts.append(
                    chunk.get("response")
                    or chunk.get("text")
                    or ""
                )

            else:
                answer_parts.append(str(chunk))

        answer = "".join(answer_parts).strip()

        if not answer:
            answer = "I don't know based on the documents."

        return {
            "answer": answer,
            "sources": results
        }

    except Exception as e:

        traceback.print_exc()

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }


# =====================================
# FILE UPLOAD
# =====================================
from fastapi import UploadFile, File
import tempfile
import os

from app.ingestion.ingest import ingest_file, get_file_hash, file_exists,chunk_text,get_upserter, get_store


from fastapi import UploadFile, File
import tempfile
import os
import traceback

from app.ingestion.ingest import ingest_file
import os
import pandas as pd
from datetime import datetime

UPLOAD_HISTORY_FILE = "upload_history.csv"


def save_history(filename, chunks=0, file_hash=""):

    row = {
        "filename": filename,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "chunks": chunks,
        "file_hash": file_hash
    }

    try:

        if os.path.exists(UPLOAD_HISTORY_FILE):

            df = pd.read_csv(UPLOAD_HISTORY_FILE)

        else:

            df = pd.DataFrame(
                columns=[
                    "filename",
                    "date",
                    "time",
                    "chunks",
                    "file_hash"
                ]
            )

        df = pd.concat(
            [df, pd.DataFrame([row])],
            ignore_index=True
        )

        df.to_csv(
            UPLOAD_HISTORY_FILE,
            index=False
        )

        print("✅ HISTORY SAVED")
        print(df.tail())

    except Exception as e:

        print("❌ HISTORY SAVE ERROR:", e)
        traceback.print_exc()
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    print("UPLOAD STEP 1")

    temp_path = None

    try:

        print("UPLOAD STEP 2")

        # preserve extension
        suffix = os.path.splitext(file.filename)[1]

        print("UPLOAD FILENAME:", file.filename)

        # save uploaded file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            contents = await file.read()

            print("UPLOAD SIZE:", len(contents))

            tmp.write(contents)

            temp_path = tmp.name

        print("UPLOAD STEP 3")
        print("TEMP PATH:", temp_path)

        # call ingestion
        print("BEFORE INGEST")

        result = ingest_file(
            temp_path,
            file.filename
        )
        print("STEP H BEFORE CSV SAVE")
        print("AFTER INGEST")
        save_history(
            filename=result["filename"],
            chunks=result["chunks"],
            file_hash=result["file_hash"]
        )

        print("UPLOAD STEP 4")
        print("INGEST RESULT:", result)

        return result

    except Exception as e:

        print("UPLOAD ERROR")
        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

    finally:

        print("UPLOAD STEP 5")

        if temp_path and os.path.exists(temp_path):

            try:

                os.remove(temp_path)

                print("TEMP FILE REMOVED")

            except Exception as cleanup_error:

                print(
                    "TEMP FILE CLEANUP ERROR:",
                    cleanup_error
                )
