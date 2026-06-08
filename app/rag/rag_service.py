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
        print("LLM ERROR:", e)
        return "An internal AI error occurred."


# =============================
# RETRIEVAL
# =============================
def retrieve(question, top_k=5):

    try:

        query_vector = embed_texts([question])[0]

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

            contexts.append(text)

            citations.append({
                "source": payload.get(
                    "source",
                    "unknown"
                ),
                "score": float(
                    getattr(r, "score", 0)
                )
            })

        context = "\n\n".join(contexts)

        return context, citations

    except Exception as e:

        print("❌ Retrieval Error:", e)

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