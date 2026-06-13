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

    query_vector = embed_texts([query])[0]

    vector_results = store.search(
        query_vector,
        top_k=10
    )

    if not vector_results:
        return []

    docs = []

    for r in vector_results:

        payload = r.get("payload", {})

        text = payload.get("text", "")

        if not text:
            continue

        docs.append({
            "text": clean_text(text),
            "score": float(r.get("score", 0)),
            "source": payload.get(
                "source",
                "unknown"
            ),
            "chunk_id": payload.get(
                "chunk_id",
                -1
            )
        })

    if not docs:
        return []

    tokenized = [
        d["text"].split()
        for d in docs
    ]

    bm25 = BM25Okapi(tokenized)

    scores = bm25.get_scores(
        query.split()
    )

    for i in range(len(docs)):
        docs[i]["bm25"] = float(scores[i])

    docs.sort(
        key=lambda x:
        x["score"] * 0.7 +
        x["bm25"] * 0.3,
        reverse=True
    )

    return docs[:5]