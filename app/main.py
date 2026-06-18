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

        IMPORTANT:

        Answer ONLY using the provided context.

        If the answer is not contained in the context,
        respond exactly:

        I don't know based on the documents.

        Return format:

        1. If code is needed → show code first

        2. Then write:
        Explanation: <1-2 lines max>

        Rules:
        - No introduction
        - No repetition
        - No extra paragraphs
        - Do NOT use outside knowledge

        Context:
        {context}

        Question:
        {req.q}

        Answer:
        """
        print("========== CONTEXT ==========")

        for r in results:
            print(
                r["source"],
                r["final_score"]
            )

            print(r["text"][:300])

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
        result = ingest_file(
            temp_path,
            file.filename
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
