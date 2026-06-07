import ollama

from app.embeddings.local_embedder import LocalEmbedder
from app.vectorstores.qdrant_store import QdrantStore
from app.config import *
from functools import lru_cache
@lru_cache(maxsize=1000)
def cached_embed(text):
    return embedder.embed([text])[0]
# -----------------------------
# INIT
# -----------------------------
embedder = LocalEmbedder(EMBED_MODEL)

store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)


# -----------------------------
# RETRIEVE CONTEXT + CITATIONS
# -----------------------------
def retrieve_context(question, top_k=5):

    #query_vector = embedder.embed([question])[0]
    query_vector = cached_embed(question)

    results = store.search(query_vector, top_k=top_k)

    contexts = []
    citations = []

    for r in results:

        payload = r.payload or {}

        text = payload.get("text", "")
        source = payload.get("source", "unknown")
        chunk_id = payload.get("chunk_id", -1)

        if text:

            contexts.append(text)

            citations.append({
                "source": source,
                "chunk_id": chunk_id,
                "preview": text[:250]
            })

    return "\n\n".join(contexts), citations


# -----------------------------
# OLLAMA LLM GENERATION
# -----------------------------
def generate_answer(prompt):

    response = ollama.chat(
        model="llama3",  # or "mistral"
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict teaching assistant. "
                    "Answer ONLY using the provided context. "
                    "If the answer is not in the context, say: "
                    "'I don't know based on the documents.'"
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
# MAIN RAG FUNCTION
# -----------------------------
def answer_question(question):

    # 1. Retrieve
    context, citations = retrieve_context(question)

    # 2. Build prompt
    prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not in the context, say:
"I don't know based on the documents."

---

Context:
{context}

---

Question:
{question}

Answer clearly and concisely:
"""

    # 3. Generate answer
    answer = generate_answer(prompt)

    # 4. Return both answer + citations
    return answer, citations