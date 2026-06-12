from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os

print("🔥 RAG v4 STARTING (CLEAN BOOT)")

app = FastAPI()


# =========================
# LAZY IMPORTS ONLY
# =========================
def get_hybrid_search():
    from app.retrieval.hybrid_search import hybrid_search_impl
    return hybrid_search_impl


def get_ingest():
    from app.ingestion.ingest import ingest_file
    return ingest_file


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"status": "ok", "version": "v4"}


@app.head("/")
def head():
    return ""


# =========================
# QUERY MODEL
# =========================
class QueryRequest(BaseModel):
    q: str


# =========================
# QUERY ENDPOINT
# =========================
@app.post("/query")
def query(req: QueryRequest):

    try:
        hybrid_search = get_hybrid_search()

        docs = hybrid_search(req.q)

        context = "\n\n".join(
            [d.get("text", "") for d in docs]
        )[:2500]

        answer = f"Context:\n{context}\n\nQ:{req.q}"

        return {
            "answer": answer,
            "sources": docs
        }

    except Exception as e:
        return {
            "error": str(e)
        }

def run_ingestion(path: str, filename: str):

    try:
        ingest_file = get_ingest()

        import asyncio

        class FakeUpload:
            def __init__(self, path, filename):
                self.filename = filename
                self.path = path

            async def read(self):
                with open(self.path, "rb") as f:
                    return f.read()

        file = FakeUpload(path, filename)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(ingest_file(file))

        print("🔥 ingestion complete:", filename)

    except Exception as e:
        print("❌ ingestion error:", e)

# =========================
# INGEST (ASYNC SAFE)
# =========================

from fastapi import BackgroundTasks
@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):

    try:
        ingest_file = get_ingest()

        # SAVE FILE FIRST (FAST)
        temp_path = f"/tmp/{file.filename}"

        content = await file.read()

        with open(temp_path, "wb") as f:
            f.write(content)

        # 🔥 RETURN IMMEDIATELY (IMPORTANT FIX)
        background_tasks.add_task(run_ingestion, temp_path, file.filename)

        return {
            "success": True,
            "message": "File received. Processing in background."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }