from sentence_transformers import CrossEncoder


# ==============================
# LOAD MODEL
# ==============================
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ==============================
# RERANK
# ==============================
def rerank_results(
    query,
    results,
    top_k=5
):

    if not results:
        return []

    pairs = []

    for r in results:

        pairs.append(
            [query, r["text"]]
        )

    scores = reranker.predict(pairs)

    # attach scores
    for i in range(len(results)):

        results[i]["rerank_score"] = float(
            scores[i]
        )

    # sort by rerank score
    results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return results[:top_k]
