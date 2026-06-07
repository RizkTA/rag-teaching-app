from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.embeddings.api_embedder import embed_texts

# try to load Qdrant safely
try:
    from app.vectorstores.qdrant_store import QdrantStore

    store = QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

except Exception as e:
    print("⚠️ Qdrant disabled or failed:", e)
    store = None


def hybrid_search(query, top_k=5):

    # -----------------------------
    # FALLBACK MODE (NO QDRANT)
    # -----------------------------
    if store is None:
        return [
            {
                "text": f"🧠 AI fallback answer: {query}",
                "score": 1.0,
                "source": "fallback"
            }
        ]

    try:
        # -----------------------------
        # VECTOR SEARCH
        # -----------------------------
        q_vec = embed_texts([query])[0]
        results = store.search(q_vec, top_k=top_k)

        output = []
        for r in results:
            payload = r.payload or {}

            output.append({
                "text": payload.get("text", ""),
                "score": getattr(r, "score", 0),
                "source": payload.get("source", "unknown"),
                "chunk_id": payload.get("chunk_id", 0)
            })

        return output

    except Exception as e:
        return [
            {
                "text": f"System error: {str(e)}",
                "score": 1.0,
                "source": "error"
            }
        ]