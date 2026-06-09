from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM,
)

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


# -----------------------------
# INIT QDRANT
# -----------------------------
store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


# -----------------------------
# RETRIEVE CONTEXT
# -----------------------------
def retrieve_context(question, top_k=5):

    try:

        # embed query
        query_vector = embed_texts([question])[0]

        # search qdrant
        results = store.search(
            query_vector,
            top_k=top_k
        )

        contexts = []
        citations = []

        for r in results:

            payload = r.payload or {}

            text = payload.get("text", "")
            source = payload.get("source", "unknown")
            chunk_id = payload.get("chunk_id", -1)

            if not text:
                continue

            contexts.append(text)

            citations.append({
                "source": source,
                "chunk_id": chunk_id,
                "score": float(getattr(r, "score", 0))
            })

        context = "\n\n".join(contexts)

        return context, citations

    except Exception as e:

        print("❌ Retrieval Error:", e)

        return "", []