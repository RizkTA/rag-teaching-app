from sentence_transformers import CrossEncoder

# =========================
# LOAD MODEL ONCE
# =========================
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# =========================
# RERANK FUNCTION
# =========================
def rerank_results(query, results, top_k=5):

    if not results:
        return []

    # Build query-document pairs
    pairs = [
        (query, r["text"])
        for r in results
    ]

    # Predict relevance
    scores = reranker_model.predict(pairs)

    # Attach reranker scores
    for r, score in zip(results, scores):

        r["rerank_score"] = float(score)

    # Sort descending
    results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return results[:top_k]