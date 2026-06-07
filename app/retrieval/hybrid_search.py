from app.config import QDRANT_ENABLED, QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.embeddings.api_embedder import embed_texts

store = None


class QDRANTStore:
    pass


if QDRANT_ENABLED:
    try:
        from app.vectorstores.qdrant_store import QdrantStore
        store = QDRANTStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)
    except Exception as e:
        print("⚠️ Qdrant disabled:", e)
        store = None


def hybrid_search(query, top_k=5):

    # =========================
    # FALLBACK MODE (NO QDRANT)
    # =========================
    if store is None:
        return [
            {
                "text": f"🧠 AI fallback answer: {query}",
                "score": 1.0,
                "source": "fallback"
            }
        ]

    # real search
    try:
        q_vec = embed_texts([query])[0]
        results = store.search(q_vec, top_k=top_k)

        return [
            {
                "text": r.payload.get("text", ""),
                "score": getattr(r, "score", 0),
                "source": r.payload.get("source", "unknown")
            }
            for r in results
        ]

    except Exception as e:
        return [
            {
                "text": f"System error fallback: {str(e)}",
                "score": 1.0,
                "source": "error"
            }
        ]