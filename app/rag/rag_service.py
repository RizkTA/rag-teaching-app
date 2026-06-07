from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM,
    GROQ_API_KEY
)

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore
from groq import Groq


# =============================
# GROQ CLIENT
# =============================
client = Groq(api_key=GROQ_API_KEY)


# =============================
# CONFIG
# =============================
MAX_CONTEXT_CHARS = 6000
TOP_K = 5


# =============================
# INIT VECTOR DB
# =============================
try:
    store = QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

    print("✅ Qdrant connected")

except Exception as e:

    print("⚠️ Qdrant disabled:", e)

    store = None


# =============================
# LLM GENERATION
# =============================
def generate(prompt: str) -> str:

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful teaching assistant. "
                        "Answer ONLY using the provided context."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"LLM error: {str(e)}"


# =============================
# RETRIEVAL
# =============================
def retrieve(question: str, top_k=TOP_K):

    if store is None:
        return "", []

    try:

        # embed query
        query_vector = embed_texts([question])[0]

        # vector search
        results = store.search(
            query_vector,
            top_k=top_k
        )

        contexts = []
        citations = []

        for r in results:

            payload = r.payload or {}

            text = payload.get("text", "")

            if not text:
                continue

            score = float(getattr(r, "score", 0))

            contexts.append(text)

            citations.append({
                "source": payload.get("source", "unknown"),
                "chunk_id": payload.get("chunk_id", -1),
                "score": score,
                "preview": text[:200]
            })

        context = "\n\n".join(contexts)

        context = context[:MAX_CONTEXT_CHARS]

        return context, citations

    except Exception as e:

        print("❌ Retrieval error:", e)

        return "", []


# =============================
# MAIN RAG FUNCTION
# =============================
def answer(question: str):

    # retrieve docs
    context, citations = retrieve(question)

    # no docs fallback
    if not context.strip():

        return {
            "answer": "I don't know based on the documents.",
            "citations": [],
            "context_length": 0
        }

    # prompt
    prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not contained in the context,
say:
"I don't know based on the documents."

----------------

Context:
{context}

----------------

Question:
{question}

Answer clearly and concisely.
"""

    # generate answer
    answer_text = generate(prompt)

    return {
        "answer": answer_text,
        "citations": citations,
        "context_length": len(context)
    }