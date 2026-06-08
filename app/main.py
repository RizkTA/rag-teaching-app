print("🔥 MAIN.PY STARTING")
from fastapi import FastAPI
from pydantic import BaseModel

from app.llm.streaming import stream_answer
print("🔥 IMPORTS SUCCESS")
app = FastAPI()

# =================================
# ROOT HEALTH CHECK
# =================================
@app.get("/")
def root():

    return {
        "status": "ok",
        "message": "RIZK AI Backend Running"
    }


@app.head("/")
def root_head():

    return {}

class QueryRequest(BaseModel):
    q: str


@app.get("/")
def root():
    return {"status": "ok", "message": "RAG SaaS v2 running"}

from fastapi import UploadFile, File
import shutil
import os

from app.ingestion.ingest import ingest_pdf


# =================================
# PDF UPLOAD + INGEST
# =================================
@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    try:

        # create data folder
        os.makedirs("data", exist_ok=True)

        # save uploaded file
        save_path = f"data/{file.filename}"
        #save_path = f"/data/{file.filename}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(f"✅ File saved: {save_path}")

        # ingest into qdrant
        result = ingest_pdf(save_path)

        print("🔥 INGEST RESULT:", result)

        return {
            "success": True,
            "filename": file.filename,
            "ingest_result": result
        }

    except Exception as e:

        print("❌ Upload failed:", e)

        return {
            "success": False,
            "error": str(e)
        }


@app.post("/query")
def query(req: QueryRequest):

    try:
        results = hybrid_search(req.q)

        context = "\n\n".join([r["text"] for r in results])[:2500]

        prompt = f"Context:\n{context}\n\nQuestion:\n{req.q}"

        answer = "".join(stream_answer(prompt))

        return {
            "answer": answer,
            "sources": results
        }

    except Exception as e:
        return {
            "answer": f"System fallback response: {str(e)}",
            "sources": []
        }