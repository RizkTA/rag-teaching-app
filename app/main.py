from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

import os
import tempfile
import traceback

print("🔥 BEFORE INGEST IMPORT")

from app.ingestion.ingest import ingest_file

print("🔥 AFTER INGEST IMPORT")
print("🔥 MAIN.PY LOADED")

from app.rag.fusion_rag import fusion_search
from app.llm.streaming import stream_answer

# =====================================
# FASTAPI
# =====================================
app = FastAPI()


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

        if not results:
            return {
                "answer": "I don't know based on the documents.",
                "sources": []
            }

        context = "\n\n".join(
            [r["text"] for r in results]
        )[:2500]

        prompt = f"""
You are a helpful teaching assistant.

Return format:

1. If code is needed → show code first

2. Then write:
Explanation: <1-2 lines max>

Rules:
- No introduction
- No repetition
- No extra paragraphs

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
from fastapi import UploadFile, File
import tempfile
import os

from app.ingestion.ingest import ingest_file


@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...)
):

    print("🔥 ENDPOINT HIT")
    print("🔥 filename:", file.filename)

    temp_path = None

    try:

        suffix = os.path.splitext(
            file.filename
        )[1]

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
        print("RESULT =", result)

        return result

    except Exception as e:

        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        try:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as cleanup_error:

            print(
                "⚠️ temp file cleanup failed:",
                cleanup_error
            )