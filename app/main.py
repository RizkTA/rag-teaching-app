from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import os

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
# HEALTH CHECK (CRITICAL FOR RENDER)
# =========================
@app.get("/")
def root():
    return {"status": "ok"}


@app.head("/")
def head():
    return ""


# =========================
# QUERY
# =========================
class QueryRequest(BaseModel):
    q: str


@app.post("/query")
def query(req: QueryRequest):

    try:
        hybrid_search = get_hybrid_search()
        docs = hybrid_search(req.q)

        context = "\n\n".join(
            d.get("text", "") for d in docs
        )[:2500]

        return {
            "answer": context,
            "sources": docs
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# INGEST (ASYNC SAFE)
# =========================
@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):

    ingest_file = get_ingest()

    content = await file.read()

    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(content)

    background_tasks.add_task(ingest_file, path, file.filename)

    return {
        "success": True,
        "message": "Processing started in background"
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )