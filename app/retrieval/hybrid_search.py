from rank_bm25 import BM25Okapi
from app.core.lazy import get_store, embed_texts, get_reranker
from app.retrieval.query_expansion import expand_query


def hybrid_search_impl(query: str):

    store = get_store()

    expanded = expand_query(query)

    # ======================
    # VECTOR SEARCH
    # ======================
    query_vec = embed_texts([expanded])[0]

    results = store.search(query_vec, top_k=15)

    docs = []
    for r in results:
        score = r.get("score", 0.0)
        if score < 0.45:
            continue

        payload = r.get("payload", {})
        payload["score"] = score
        docs.append(payload)

    if not docs:
        return []

    # ======================
    # BM25
    # ======================
    tokenized = [d["text"].split() for d in docs]
    bm25 = BM25Okapi(tokenized)

    bm25_scores = bm25.get_scores(query.split())

    for i in range(len(docs)):
        docs[i]["bm25"] = float(bm25_scores[i])

    # ======================
    # COMBINE SCORE
    # ======================
    docs.sort(
        key=lambda x: x["score"] * 0.7 + x["bm25"] * 0.3,
        reverse=True
    )

    # ======================
    # FINAL RERANK
    # ======================
    reranker = get_reranker()

    pairs = [(query, d["text"]) for d in docs[:10]]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(docs[:10], scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [d[0] for d in ranked[:5]]
