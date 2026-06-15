from app.embeddings.api_embedder import embed_texts

from app.vectorstores.qdrant_store import QdrantStore

from app.config import (
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


# ==============================
# INIT QDRANT
# ==============================
def get_store():
    return QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)


# ==============================
# DETECT QUERY LANGUAGE
# ==============================
def detect_query_language(query):

    q = query.lower()

    if "c++" in q or "cpp" in q:
        return "cpp"

    elif "python" in q or "py" in q:
        return "python"

    return None


# ==============================
# VECTOR SEARCH
# ==============================
def vector_search(
    query,
    top_k=5
):

    # ==========================
    # DETECT LANGUAGE
    # ==========================
    language = detect_query_language(query)

    # ==========================
    # EMBED QUERY
    # ==========================
    query_vector = embed_texts([query])[0]

    # ==========================
    # SEARCH QDRANT
    # ==========================
    results = store.search(
        query_vector=query_vector,
        top_k=top_k,
        language=language
    )

    formatted = []

    for r in results:

        payload = r.payload or {}

        formatted.append({

            "text": payload.get(
                "text",
                ""
            ),

            "source": payload.get(
                "source",
                "unknown"
            ),

            "score": float(
                getattr(r, "score", 0)
            ),

            "language": payload.get(
                "language",
                "text"
            ),

            "topic": payload.get(
                "topic",
                "general"
            )
        })

    return formatted