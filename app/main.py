from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

print("🔥 MAIN.PY STARTING")

# ==============================
# IMPORTS
# ==============================
from app.retrieval.hybrid_search import hybrid_search
from app.llm.streaming import stream_answer
from app.ingestion.ingest import ingest_file

print("🔥 IMPORTS SUCCESS")

# ==============================
# APP
# ==============================
app = FastAPI()


# ==============================
# HEALTH CHECK
# ==============================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "RIZK AI Backend Running"
    }


@app.head("/")
def root_head():
    return {}


# ==============================
# REQUEST MODEL
# ==============================
class QueryRequest(BaseModel):
    q: str


# ==============================
# QUERY ENDPOINT
# ==============================
@app.post("/query")
def query(req: QueryRequest):

    try:
        # 1. retrieve
        results = hybrid_search(req.q)

        # 2. build context
        context = "\n\n".join(
            [r.get("text", "") for r in results if r.get("text")]
        )[:4000]

        # 3. prompt
        prompt = f"""
Use ONLY the context below to answer.

If the answer is not in the context, say:
"I don't know based on the documents."

Context:
{context}

Question:
{req.q}

Answer:
"""

        # 4. generate
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


# ==============================
# UNIVERSAL INGEST (PDF/MD/TXT)
# ==============================
from fastapi import UploadFile, File
import os

from app.ingestion.ingest import ingest_file


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    try:
        # ==============================
        # 1. GET FILE EXTENSION (FIX)
        # ==============================
        if not file.filename or "." not in file.filename:
            return {
                "success": False,
                "error": "Invalid file name"
            }

        ext = file.filename.split(".")[-1].lower()

        allowed_ext = ["pdf", "md", "txt"]

        if ext not in allowed_ext:
            return {
                "success": False,
                "error": f".{ext} files are not supported"
            }

        # ==============================
        # 2. INGEST FILE (UNIVERSAL PIPELINE)
        # ==============================
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