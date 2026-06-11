from rank_bm25 import BM25Okapi

from app.embeddings.api_embedder import embed_texts
from app.retrieval.query_expansion import expand_query
from app.retrieval.reranker import rerank
from app.vectorstores.store_provider import get_store


def hybrid_search(query):

    store = get_store()

    # 1. expand query
    expanded = expand_query(query)

    # 2. vector search
    query_vector = embed_texts([expanded])[0]

    vector_results = store.search(query_vector, top_k=15)

    if not vector_results:
        return []

    docs = []

    for r in vector_results:

        score = r.get("score", 0.0)
        payload = r.get("payload", {})

        if score < 0.45:
            continue

        payload["score"] = score
        docs.append(payload)

    if not docs:
        return []

    # 3. BM25
    tokenized = [d["text"].split() for d in docs]

    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())

    for i in range(len(docs)):
        docs[i]["bm25"] = float(bm25_scores[i])

    # 4. merge scoring
    docs = sorted(
        docs,
        key=lambda x: x["score"] * 0.7 + x["bm25"] * 0.3,
        reverse=True
    )

    # 5. rerank
    reranked = rerank(query, docs[:10])

    return reranked[:5]