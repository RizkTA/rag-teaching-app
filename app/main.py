import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi import Form
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
from app.history.history import save_history
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

from fastapi import UploadFile, File, Form, HTTPException
import os
import tempfile
import traceback

@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    replace_existing: bool = Form(False)
):

    temp_path = None

    try:

        print("=" * 80)
        print("UPLOAD STARTED")
        print("Filename:", file.filename)
        print("Replace Existing:", replace_existing)

        suffix = os.path.splitext(file.filename)[1]
        filename = file.filename

        contents = await file.read()

        print("File Size:", len(contents))

        if len(contents) == 0:
            raise Exception("Uploaded file is empty")

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(contents)
            temp_path = tmp.name

        print("Temporary File:", temp_path)

        # -------------------------
        # INGEST
        # -------------------------

        print("CALLING INGEST_FILE")

        result = ingest_file(
            temp_path,
            filename,
            replace_existing
        )

        print("INGEST RESULT:")
        print(result)

        if not isinstance(result, dict):

            raise Exception(
                f"ingest_file returned {type(result)} instead of dict"
            )

        status = result.get("status")

        # -------------------------
        # SUCCESS
        # -------------------------

        if status in ["ok", "uploaded"]:

            save_history(
                filename=result.get(
                    "filename",
                    filename
                ),
                status="uploaded",
                filetype=suffix.replace(".", ""),
                chunks=result.get(
                    "chunks",
                    0
                ),
                file_hash=result.get(
                    "file_hash",
                    ""
                )
            )

            print("HISTORY SAVED")

            return result

        # -------------------------
        # SKIPPED
        # -------------------------

        if status == "skipped":

            save_history(
                filename=filename,
                status="skipped",
                filetype=suffix.replace(".", ""),
                chunks=0,
                file_hash=result.get(
                    "file_hash",
                    ""
                )
            )

            return result

        # -------------------------
        # ERROR FROM INGEST
        # -------------------------

        save_history(
            filename=filename,
            status="failed",
            filetype=suffix.replace(".", ""),
            chunks=0,
            file_hash=""
        )

        raise HTTPException(
            status_code=500,
            detail=result.get(
                "message",
                "Unknown ingest error"
            )
        )

    except Exception as e:

        print("UPLOAD ERROR")
        traceback.print_exc()

        try:

            save_history(
                filename=file.filename,
                status=f"error: {str(e)}",
                filetype=file.filename.split(".")[-1],
                chunks=0,
                file_hash=""
            )

        except Exception as history_error:

            print(
                "HISTORY SAVE FAILED:",
                history_error
            )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if (
            temp_path
            and
            os.path.exists(temp_path)
        ):

            try:

                os.remove(temp_path)

            except Exception as cleanup_error:

                print(
                    "TEMP FILE CLEANUP ERROR:",
                    cleanup_error
                )