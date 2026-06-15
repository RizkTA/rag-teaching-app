from fastapi import FastAPI, UploadFile, File
print("🔥 BEFORE INGEST IMPORT")

from app.ingestion.ingest import ingest_file

print("🔥 AFTER INGEST IMPORT")
print("🔥 MAIN.PY LOADED")
app = FastAPI()


from app.rag.fusion_rag import fusion_search
from app.llm.streaming import stream_answer

from pydantic import BaseModel


class QueryRequest(BaseModel):
    q: str

app = FastAPI()

@app.get("/")
def root():

    return {
        "status": "ok"
    }


@app.head("/")
def root_head():

    return

@app.post("/query")
def query(req: QueryRequest):

    try:
        #results = hybrid_search_impl(req.q)
        results = fusion_search(req.q)
        if not results:
            return {
                "answer": "I don't know based on the documents.",
                "sources": []
            }

        context = "\n\n".join([r["text"] for r in results])[:2500]

        prompt = f"""
You are a helpful teaching assistant.
Return format:

1. If code is needed → show code first

2. Then write: Explanation: <1-2 lines max>

Rules:
- No **Code:** None needed!
- No introduction
- No extra paragraphs
- No repetition
- Give a clear and natural answer

Context:
{context}

Question:
{req.q}


Answer:
"""
        answer_parts = []

        for chunk in stream_answer(prompt):
            if isinstance(chunk, dict):
                answer_parts.append(
                    chunk.get("response") or chunk.get("text") or ""
                )
            else:
                answer_parts.append(str(chunk))

        answer = "".join(answer_parts).strip()

        # ONLY fallback check (no stripping, no prefix removal)
        if not answer:
            answer = "I don't know based on the documents."

        return {
            "answer": answer,
            "sources": results
        }
    # ✅ THIS IS REQUIRED
    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }
from fastapi import UploadFile, File
from app.ingestion.ingest import ingest_file

# =================================
# FILE UPLOAD ENDPOINT
# =================================


from fastapi import UploadFile, File
import tempfile
import os

from app.ingestion.ingest import ingest_file
@app.get("/health")
async def health():

    return {
        "status": "ok"
    }

# ADD THIS TEMPORARILY
@app.get("/test")
def test():

    print("🔥 TEST ENDPOINT HIT")

    return {
        "status": "test_ok"
    }
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    print("🔥 ENDPOINT HIT")
    print("🔥 filename:", file.filename)

    temp_path = None

    try:

        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            contents = await file.read()
            tmp.write(contents)

            temp_path = tmp.name

        print("🔥 temp file:", temp_path)

        print("🔥 BEFORE INGEST")

        result = ingest_file(
            temp_path,
            file.filename
        )

        print("🔥 AFTER INGEST")
        print(result)

        return result

    except Exception as e:

        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e)
        }