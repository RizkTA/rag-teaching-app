from app.retrieval.vector_search import (
    vector_search
)

from app.retrieval.bm25_search import (
    search_bm25
)

from app.retrieval.reranker import (
    rerank_results
)


# ==============================
# HYBRID SEARCH
# ==============================
def hybrid_search(query):

    # ==========================
    # VECTOR SEARCH
    # ==========================
    semantic = vector_search(
        query,
        top_k=8
    )

    # ==========================
    # BM25 SEARCH
    # ==========================
    keyword = search_bm25(
        query,
        top_k=8
    )

    # ==========================
    # MERGE
    # ==========================
    combined = semantic + keyword

    # ==========================
    # REMOVE DUPLICATES
    # ==========================
    seen = set()

    unique = []

    for r in combined:

        text = r["text"]

        if text not in seen:

            seen.add(text)

            unique.append(r)

    # ==========================
    # RERANK
    # ==========================
    reranked = rerank_results(
        query,
        unique,
        top_k=5
    )

    return reranked