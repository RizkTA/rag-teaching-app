import ollama

from app.embeddings.local_embedder import LocalEmbedder
from app.vectorstores.qdrant_store import QdrantStore
from app.config import *

# -----------------------------
# CONFIG
# -----------------------------
MAX_CONTEXT_CHARS = 6000  # increased for better answers
MIN_SCORE = 0.15

# -----------------------------
# SINGLETONS
# -----------------------------
embedder = LocalEmbedder(EMBED_MODEL)
store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)


# -----------------------------
# RETRIEVAL
# -----------------------------
def retrieve(question, top_k=5, min_score=MIN_SCORE):

    query_vector = embedder.embed([question])[0]
    results = store.search(query_vector, top_k=top_k)

    contexts = []
    citations = []

    for r in results:

        score = getattr(r, "score", 0)

        payload = r.payload or {}
        text = payload.get("text", "")
        source = payload.get("source", "unknown")
        chunk_id = payload.get("chunk_id", -1)

        # keep more recall (do NOT over-filter)
        if not text:
            continue

        contexts.append(text)

        citations.append({
            "source": source,
            "chunk_id": chunk_id,
            "score": float(score),
            "preview": text[:200]
        })

    context = "\n\n".join(contexts)

    # safer truncation (avoid breaking sentences too much)
    context = context[:MAX_CONTEXT_CHARS]

    return context, citations


# -----------------------------
# LLM
# -----------------------------
def generate(prompt):

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful teaching assistant. "
                    "Answer ONLY using the provided context. "
                    "If the context is insufficient, say you don't know."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------
# MAIN ANSWER FUNCTION
# -----------------------------
def answer(question):

    context, citations = retrieve(question)

    # 🚨 FIX: only ONE fallback rule (no confusion)
    if not context.strip():
        return {
            "answer": "I don't know based on the documents.",
            "citations": [],
            "context_length": 0
        }

    prompt = f"""
Use the context below to answer the question.

Context:
{context}

Question:
{question}

Provide a clear explanation.
If the answer is partially in context, infer carefully.
"""

    answer_text = generate(prompt)

    return {
        "answer": answer_text,
        "citations": citations,
        "context_length": len(context)
    }