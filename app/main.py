from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Query
import psutil
import os
import threading

from app.jobs import get_job, list_jobs, update_job, create_job, finish_job,delete_job,fail_job
from app.ingestion.chunker import stream_chunks

print(
    "MEMORY MB:",
    psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
)
print("🔥 BEFORE INGEST IMPORT")

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
from app.history import delete_uploaded_file
import subprocess

@app.get("/job/{job_id}")
def job_status(job_id: str):

    job = get_job(job_id)

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
@app.get("/jobs")
def jobs():

    return list_jobs()
@app.get("/upload_progress/{job_id}")
def upload_progress(job_id: str):

    job = get_job(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
@app.get("/ocr_check")
def ocr_check():
    def version(cmd):
        try:
            return subprocess.check_output(cmd).decode().splitlines()[0]
        except Exception as e:
            return str(e)

    return {
        "tesseract": version(["tesseract", "--version"]),
        "ghostscript": version(["gs", "--version"]),
        "ocrmypdf": version(["ocrmypdf", "--version"])
    }
@app.delete("/delete_file")
def delete_file(file_hash: str):

    delete_uploaded_file(file_hash)

    return {
            "status": "deleted",
            "file_hash": file_hash
        }


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


@app.get("/versions")
def versions():
    import numpy

    import huggingface_hub

    return {
        "numpy": numpy.__version__,

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

@app.get("/debug_sources")
def debug_sources():

    store = get_store()

    points, _ = store.client.scroll(
        collection_name=os.getenv("QDRANT_COLLECTION", "docs"),
        limit=20,
        with_payload=True
    )

    return [
        p.payload.get("source")
        for p in points
    ]
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

from app.ingestion.ingest import get_store

from app.ingestion.ingest import ingest_file

from fastapi import UploadFile, File, Form, HTTPException

from app.history import load_history, save_history, save_uploaded_file
import os
import tempfile
import traceback
from app.history import get_uploaded_files
import threading
@app.get("/uploaded_files")
def uploaded_files():

    df = get_uploaded_files()

    return df.to_dict(orient="records")
def background_ingest(
    temp_path,
    filename,
    replace_existing,
    job_id
):

    try:

        result = ingest_file(

            temp_path,

            filename,

            replace_existing,

            job_id=job_id

        )

        if result["status"] == "ok":

            save_uploaded_file(

                filename=filename,

                file_hash=result["file_hash"],

                chunks=result["chunks"]

            )

            save_history(

                filename=filename,

                status="uploaded",

                filetype=filename.split(".")[-1].lower(),

                chunks=result["chunks"],

                file_hash=result["file_hash"]

            )

            finish_job(job_id)

        else:

            fail_job(

                job_id,

                result.get("message", "Upload failed")

            )

    except Exception as e:

        traceback.print_exc()

        fail_job(job_id, str(e))

    finally:

        try:
            os.remove(temp_path)
        except Exception:
            pass
@app.get("/job/{job_id}")
async def job_status(job_id: str):

    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    replace_existing: bool = Form(False)
):

    print("UPLOAD STEP 1")

    try:

        print("UPLOAD STEP 2")

        suffix = os.path.splitext(file.filename)[1]

        filename = file.filename

        print("UPLOAD FILENAME:", filename)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            total_size = 0

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                tmp.write(chunk)

            temp_path = tmp.name

        print("UPLOAD SIZE MB:", round(total_size / 1024 / 1024, 2))

        print("TEMP PATH:", temp_path)

        # -----------------------------------------
        # Create background job
        # -----------------------------------------

        job_id = create_job(filename)

        def worker():

            try:

                result = ingest_file(

                    temp_path,

                    filename,

                    replace_existing,

                    job_id

                )

                if result["status"] == "ok":

                    save_uploaded_file(

                        filename=filename,

                        file_hash=result["file_hash"],

                        chunks=result["chunks"]

                    )

                    save_history(

                        filename=filename,

                        status="uploaded",

                        filetype=filename.split(".")[-1],

                        chunks=result["chunks"],

                        file_hash=result["file_hash"]

                    )

                    finish_job(job_id)

                else:

                    fail_job(

                        job_id,

                        result.get("message", "Unknown error")

                    )

            except Exception as e:

                fail_job(job_id, str(e))

            finally:

                try:
                    os.remove(temp_path)
                except:
                    pass

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

        print("✅ Background ingestion started")

        # -----------------------------------------
        # Return immediately
        # -----------------------------------------

        return {

            "status": "started",

            "job_id": job_id

        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )