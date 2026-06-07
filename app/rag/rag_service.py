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
# GROQ CLIENT (LLM)
# =============================
client = Groq(api_key=GROQ_API_KEY)


def generate(prompt: str) -> str:
    """
    LLM generator using Groq (production safe)
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful teaching assistant. Use ONLY the provided context."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"LLM error: {str(e)}"


# =============================
# CONFIG
# =============================
MAX_CONTEXT_CHARS = 6000


# =============================
# INIT VECTOR DB
# =============================
try:
    store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)
except Exception as e:
    print("⚠️ Qdrant disabled:", e)
    store = None


# =============================
# RETRIEVAL
# =============================
def retrieve(question, top_k=5):
    if store is None:
        return "", []

    try:
        query_vector = embed_texts([question])[0]
        results = store.search(query_vector, top_k=top_k)

        contexts = []
        citations = []

        for r in results:
            payload = r.payload or {}
            text = payload.get("text", "")

            if not text:
                continue

            contexts.append(text)

            citations.append({
                "source": payload.get("source", "unknown"),
                "chunk_id": payload.get("chunk_id", -1),
                "score": float(getattr(r, "score", 0)),
                "preview": text[:200]
            })

        context = "\n\n".join(contexts)[:MAX_CONTEXT_CHARS]

        return context, citations

    except Exception as e:
        print("❌ Retrieval error:", e)
        return "", []


# =============================
# MAIN ANSWER FUNCTION
# =============================
def answer(question: str):

    context, citations = retrieve(question)

    if not context.strip():
        return {
            "answer": "I don't know based on the documents.",
            "citations": [],
            "context_length": 0
        }

    prompt = f"""
Context:
{context}

Question:
{question}

Answer clearly using ONLY the context above.
"""

    return {
        "answer": generate(prompt),
        "citations": citations,
        "context_length": len(context)
    }