from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import tempfile
import os

PORT = int(os.getenv("PORT", 8000))
from app.llm.streaming import stream_answer
from app.retrieval.hybrid_search import hybrid_search_impl

def clean_text(text: str):
    return (
        text.replace("â", "-")
            .replace("Â", "")
            .replace("\n", " ")
            .strip()
    )
app = FastAPI()


# =========================
# MODELS
# =========================
class QueryRequest(BaseModel):
    q: str


# =========================
# HEALTH
# =========================
@app.get("/")
def root():
    return {"status": "ok", "message": "RAG v6 running"}


# =========================
# QUERY ENDPOINT (SAFE)
# =========================
@app.post("/query")
def query(req: QueryRequest):

    try:
        results = hybrid_search_impl(req.q)

        if not results:
            return {
                "answer": "I don't know based on the documents.",
                "sources": []
            }

        # =========================
        # SAFE CONTEXT BUILDING
        # =========================
        safe_texts = []
        safe_sources = []

        for r in results:
            if not isinstance(r, dict):
                continue

            text = r.get("text") or ""
            if not text:
                continue

            cleaned = clean_text(text)
            safe_texts.append(cleaned)

            safe_sources.append({
                "text": cleaned,
                "score": float(r.get("score") or 0.0),
                "source": r.get("source") or "unknown"
            })

        context = "\n\n".join(safe_texts)

        # optional safety limit (not character cut mid-sentence)
        if len(context) > 3500:
            context = context[:3500].rsplit(" ", 1)[0]

        context = context.replace("\n", " ")
        prompt = f"""
        You are a helpful teaching assistant.

        Use ONLY the context below.

        If the answer is not in the context, say:
        "I don't know based on the documents."

        Context:
        {context}

        Question:
        {req.q}

        Instructions:
        - Give a clear and natural answer
        - Be concise but complete
        - Do not repeat the question
        - Do not mention "the question is asking"
        - Do not be overly formal

        Answer:
        """

        # =========================
        # SINGLE LLM CALL (FIXED)
        # =========================
        raw_answer = stream_answer(prompt)

        answer = ""

        # CASE 1: string output
        if isinstance(raw_answer, str):
            answer = raw_answer

        # CASE 2: dict output
        elif isinstance(raw_answer, dict):
            answer = raw_answer.get("response", "")

        # CASE 3: list output
        elif isinstance(raw_answer, list):
            answer = "".join(str(x) for x in raw_answer)

        # CASE 4: generator
        else:
            try:
                for chunk in raw_answer:
                    if isinstance(chunk, dict):
                        answer += chunk.get("response", "")
                    else:
                        answer += str(chunk)
            except Exception:
                answer = str(raw_answer)

        answer = answer.strip()

        if not answer:
            answer = "I don't know based on the documents."

        return {
            "answer": answer,
            "sources": safe_sources
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }
# =========================
# UPLOAD (SAFE + SIMPLE)
# =========================
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    from app.ingestion.ingest import ingest_file

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    result = ingest_file(path, file.filename)

    return {
        "success": True,
        "details": result
    }