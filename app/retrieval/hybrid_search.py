from rank_bm25 import BM25Okapi

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.store_provider import get_store
from app.retrieval.query_expansion import expand_query
from app.retrieval.reranker import rerank


def hybrid_search_impl(query: str):

    store = get_store()

    # =====================
    # CLEAN TEXT FUNCTION
    # =====================
    def clean_text(text: str):
        return (
            text.replace("â", "-")
                .replace("Â", "")
                .replace("\n", " ")
                .strip()
        )

    # =====================
    # EXPAND QUERY
    # =====================
    expanded = expand_query(query)

    # =====================
    # VECTOR SEARCH
    # =====================
    query_vector = embed_texts([expanded])[0]

    vector_results = store.search(query_vector, top_k=20)

    if not vector_results:
        return []

    docs = []

    for r in vector_results:

        score = r.get("score", 0.0)
        payload = r.get("payload", {})

        text = payload.get("text")
        if not text:
            continue

        # 🔥 CLEAN HERE (CORRECT PLACE)
        text = clean_text(text)

        if score < 0.45:
            continue

        docs.append({
            "text": text,
            "score": float(score),
            "source": payload.get("source", "unknown"),
            "chunk_id": payload.get("chunk_id", -1)
        })

    if not docs:
        return []

    # =====================
    # BM25 LAYER
    # =====================
    tokenized = [d["text"].split() for d in docs]
    bm25 = BM25Okapi(tokenized)

    bm25_scores = bm25.get_scores(query.split())

    for i in range(len(docs)):
        docs[i]["bm25"] = float(bm25_scores[i])

    # =====================
    # COMBINE SCORE
    # =====================
    docs.sort(
        key=lambda x: x["score"] * 0.7 + x["bm25"] * 0.3,
        reverse=True
    )

    # =====================
    # FINAL RERANK
    # =====================
    try:
        return rerank(query, docs[:10])[:5]
    except Exception as e:
        print("🔥 RERANK ERROR:", e)
        return docs[:5]