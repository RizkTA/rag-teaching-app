from app.retrieval.bm25_search import search_bm25
from app.retrieval.query_expansion import expand_query
from app.retrieval.reranker import rerank_results
from app.retrieval.vector_search import vector_search


def hybrid_search(query, top_k=5):

    expanded_query = expand_query(query)

    vector_results = vector_search(
        expanded_query,
        top_k=10
    )

    bm25_results = search_bm25(
        expanded_query,
        top_k=10
    )

    # =========================
    # MERGE + DEDUP
    # =========================
    combined = {}

    for r in vector_results + bm25_results:

        text = r["text"]

        if text not in combined:

            combined[text] = r

        else:

            combined[text]["score"] = max(
                combined[text]["score"],
                r["score"]
            )

    combined_results = list(combined.values())

    # =========================
    # RERANK
    # =========================
    reranked = rerank_results(
        query=query,
        results=combined_results,
        top_k=top_k
    )

    return reranked