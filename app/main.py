from fastapi import FastAPI
from pydantic import BaseModel

from app.llm.streaming import stream_answer
from app.retrieval.hybrid_search import hybrid_search

app = FastAPI()


class QueryRequest(BaseModel):
    q: str


@app.get("/")
def root():
    return {"status": "ok", "message": "RAG SaaS v2 running"}


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