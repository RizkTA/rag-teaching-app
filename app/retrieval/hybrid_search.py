from rank_bm25 import BM25Okapi

from app.embeddings.embedder import embed_texts
from app.vectorstores.store_provider import get_store


def clean_text(text: str):

    return (
        text.replace("â", "-")
            .replace("Â", "")
            .replace("\n", " ")
            .strip()
    )
def hybrid_search_impl(query: str):

    store = get_store()

    # =====================
    # FAST EMBEDDING
    # =====================
    query_vector = embed_texts([query])[0]

    vector_results = store.search(
        query_vector,
        top_k=5   # 🔥 FAST LIMIT
    )

    if not vector_results:
        return []

    docs = []

    # =====================
    # BUILD DOCS (LIGHTWEIGHT)
    # =====================
    for r in vector_results:

        payload = r.get("payload", {})

        text = payload.get("text", "")
        text_lower = text.lower()

        if "contents" in text_lower:
            continue
        if not text:
            continue

        docs.append({
            "text": clean_text(text),
            "score": float(r.get("score", 0)),
            "source": payload.get("source", "unknown"),
            "chunk_id": payload.get("chunk_id", -1),
            "is_code": payload.get("is_code", False)
        })

    if not docs:
        return []

    # =====================
    # BM25 (FAST ON SMALL SET ONLY)
    # =====================
    tokenized = [d["text"].split() for d in docs]

    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())

    # =====================
    # FINAL SCORE (OPTIMIZED)
    # =====================
    for i, d in enumerate(docs):

        code_boost = 0.2 if d.get("is_code") else 0.0

        d["final_score"] = (
            d["score"] * 0.7 +
            float(bm25_scores[i]) * 0.3 +
            code_boost
        )

    # =====================
    # SORT FAST
    # =====================
    docs.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return docs[:5]