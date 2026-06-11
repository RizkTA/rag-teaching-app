from rank_bm25 import BM25Okapi

from app.embeddings.api_embedder import embed_texts
from app.vectorstores.qdrant_store import QdrantStore
from app.retrieval.query_expansion import expand_query
from app.retrieval.reranker import rerank
from app.config import *

store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)


def hybrid_search(query):

    # =========================
    # 1. EXPAND QUERY
    # =========================
    expanded = expand_query(query)

    # =========================
    # 2. VECTOR SEARCH
    # =========================
    query_vector = embed_texts([expanded])[0]

    vector_results = store.search(query_vector, top_k=15)

    if not vector_results:
        return []

    # =========================
    # 3. NORMALIZE DOCS
    # =========================
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

    # =========================
    # 4. BM25 LAYER
    # =========================
    tokenized_docs = [d["text"].split() for d in docs]

    bm25 = BM25Okapi(tokenized_docs)
    bm25_scores = bm25.get_scores(query.split())

    for i in range(len(docs)):
        docs[i]["bm25"] = float(bm25_scores[i])

    # =========================
    # 5. COMBINE SCORE
    # =========================
    docs = sorted(
        docs,
        key=lambda x: x["score"] * 0.7 + x["bm25"] * 0.3,
        reverse=True
    )
    if not docs:
        return [
            {
                "text": "No relevant context found in documents."
            }
        ]
    # =========================
    # 6. FINAL RERANK
    # =========================
    reranked = rerank(query, docs[:10])

    return reranked[:5]