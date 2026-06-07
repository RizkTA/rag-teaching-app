from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM
from app.embeddings.api_embedder import embed_texts

from app.vectorstores.qdrant_store import QdrantStore

store = QDRANTStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)


def hybrid_search(query, top_k=5):

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
        return [{
            "text": f"System error: {str(e)}",
            "score": 1.0,
            "source": "error"
        }]