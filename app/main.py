from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

from fastapi import UploadFile, File
import tempfile
import os

from app.ingestion.ingest import ingest_file

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
@app.get("/upload_test")
async def upload_test():

    print("🔥 upload_test reached")

    return {
        "message": "upload route server alive"
    }
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    temp_path = None

    try:

        print("🔥 UPLOAD START")

        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            contents = await file.read()

            print("🔥 FILE SIZE:", len(contents))

            tmp.write(contents)

            temp_path = tmp.name

        print("🔥 TEMP PATH:", temp_path)

        result = ingest_file(
            temp_path,
            file.filename
        )

        print("🔥 INGEST RESULT:", result)

        return result

    except Exception as e:

        import traceback

        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except:
                pass
