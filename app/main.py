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


# =========================
# INGEST (ASYNC SAFE)
# =========================
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    try:
        ingest_file = get_ingest()

        result = await ingest_file(file)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
