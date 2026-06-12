from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os

print("🔥 MAIN STARTING (ULTRA LIGHT MODE)")

# =====================================================
# FASTAPI APP
# =====================================================
app = FastAPI()


# =====================================================
# LAZY IMPORTS (CRITICAL FOR RENDER 512MB)
# =====================================================
def get_hybrid_search():
    from app.retrieval.hybrid_search import hybrid_search
    return hybrid_search


def get_stream_answer():
    from app.llm.streaming import stream_answer
    return stream_answer


def get_ingest():
    from app.ingestion.ingest import ingest_file
    return ingest_file


# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "RIZK AI Backend Running"
    }


@app.head("/")
def root_head():
    return ""


# =====================================================
# REQUEST MODEL
# =====================================================
class QueryRequest(BaseModel):
    q: str


# =====================================================
# QUERY ENDPOINT
# =====================================================
@app.post("/query")
def query(req: QueryRequest):

    try:

        print("🔥 query received")

        hybrid_search = get_hybrid_search()
        stream_answer = get_stream_answer()

        results = hybrid_search(req.q)

        context = "\n\n".join(
            [
                r.get("text", "")
                for r in results
                if r.get("text")
            ]
        )[:2500]

        prompt = f"""
Use ONLY the context below.

If the answer is not found, say:
"I don't know based on the documents."

Context:
{context}

Question:
{req.q}

Answer:
"""

        answer = "".join(
            stream_answer(prompt)
        )

        return {
            "answer": answer,
            "sources": results
        }

    except Exception as e:

        print("❌ QUERY ERROR:", str(e))

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }


# =====================================================
# INGEST ENDPOINT
# =====================================================
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    print("🔥 upload endpoint hit")

    try:

        print("🔥 filename:", file.filename)

        ingest_file = get_ingest()

        result = await ingest_file(file)

        print("🔥 ingest complete")

        return {
            "success": True,
            "details": result
        }

    except Exception as e:

        print("❌ upload error:", str(e))

        return {
            "success": False,
            "error": str(e)
        }


# =====================================================
# LOCAL RUN ONLY
# =====================================================
if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get("PORT", 10000)
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )
