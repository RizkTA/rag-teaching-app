from fastapi import FastAPI
from pydantic import BaseModel

from app.retrieval.hybrid_search import hybrid_search_impl
from app.llm.streaming import stream_answer

app = FastAPI()


class QueryRequest(BaseModel):
    q: str


@app.get("/")
def root():

    return {
        "status": "ok",
        "version": "RAG v7"
    }


@app.post("/query")
def query(req: QueryRequest):

    try:

        results = hybrid_search_impl(req.q)

        if not results:

            return {
                "answer":
                "I don't know based on the documents.",
                "sources": []
            }

        context = "\n\n".join(
            [r["text"] for r in results]
        )[:2500]

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

        answer = ""

        for chunk in stream_answer(prompt):

            if isinstance(chunk, dict):
                answer += chunk.get(
                    "response",
                    ""
                )
            else:
                answer += str(chunk)

        answer = answer.strip()

        if not answer:
            answer = (
                "I don't know based on the documents."
            )

        return {
            "answer": answer,
            "sources": results
        }

    except Exception as e:

        import traceback

        traceback.print_exc()

        return {
            "answer": f"System error: {str(e)}",
            "sources": []
        }