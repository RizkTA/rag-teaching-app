from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os

print("🔥 MAIN STARTING")

# ==========================
# APP INIT (LIGHT)
# ==========================
app = FastAPI()


# ==========================
# LAZY IMPORTS (IMPORTANT FIX)
# ==========================
def get_hybrid_search():
    from app.retrieval.oldhybrid_search import hybrid_search
    return hybrid_search


def get_stream_answer():
    from app.llm.streaming import stream_answer
    return stream_answer


def get_ingest():
    from app.ingestion.ingest import ingest_file
    return ingest_file


# ==========================
# HEALTH CHECK
# ==========================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "RIZK AI Backend Running"
    }


@app.head("/")
def root_head():
    return {}


# ==========================
# REQUEST MODEL
# ==========================
class QueryRequest(BaseModel):
    q: str


# ==========================
# QUERY ENDPOINT
# ==========================
@app.post("/query")
def query(req: QueryRequest):

    try:
        hybrid_search = get_hybrid_search()
        stream_answer = get_stream_answer()

        results = hybrid_search(req.q)

        context = "\n\n".join(
            [r.get("text", "") for r in results if r.get("text")]
        )[:3000]  # reduce memory

        prompt = f"""
Use ONLY the context below.

If not found, say "I don't know based on the documents."

Context:
{context}

Question:
{req.q}

Answer:
"""

        answer = "".join(stream_answer(prompt))

        return {
            "answer": answer,
            "sources": results
        }

    except Exception as e:
        print("❌ QUERY ERROR:", e)

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }


# ==========================
# INGEST ENDPOINT
# ==========================
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    try:
        ingest_file = get_ingest()

        if not file.filename or "." not in file.filename:
            return {"success": False, "error": "Invalid filename"}

        ext = file.filename.split(".")[-1].lower()

        if ext not in ["pdf", "md", "txt"]:
            return {"success": False, "error": "Unsupported file"}

        result = await ingest_file(file)

        return {
            "success": True,
            "filename": file.filename,
            "file_type": ext,
            "details": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }