from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore


# =============================
# INIT QDRANT
# =============================
try:

    store = QdrantStore(
        QDRANT_URL,
        QDRANT_COLLECTION,
        EMBED_DIM
    )

    print("✅ Qdrant connected")

except Exception as e:

    print("⚠️ Qdrant connection failed:", e)

    store = None


# =============================
# HYBRID SEARCH
# =============================
def hybrid_search(query, top_k=10):

    # fallback mode
    if store is None:

        return [
            {
                "text": f"Fallback answer for: {query}",
                "score": 1.0,
                "source": "fallback"
            }
        ]

    try:

        # embed query
        query_vector = embed_texts([query])[0]

        # search qdrant
        results = store.search(
            query_vector,
            top_k=top_k
        )

        output = []

        for r in results:

            payload = r.payload or {}

            output.append({
                "text": payload.get("text", ""),
                "score": float(getattr(r, "score", 0)),
                "source": payload.get("source", "unknown")
            })

        return output

    except Exception as e:

        print("❌ Hybrid search error:", e)

        return [
            {
                "text": f"Search failed: {str(e)}",
                "score": 1.0,
                "source": "error"
            }
        ]
