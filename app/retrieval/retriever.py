from app.ingestion.ingest import store
from app.embeddings.api_embedder import embed_texts
from test_query import question


def retrieve(query: str, top_k=5):

    # -----------------------------
    # EMBED QUERY
    # -----------------------------
    query_vector = embed_texts([question])[0]
    # -----------------------------
    # QDRANT SEARCH (SAFE VERSION)
    # -----------------------------
    results = store.client.search(
        collection_name=store.collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False
    )

    print("\n=== SEARCH RESULTS ===")

    contexts = []
    sources = set()

    for r in results:

        score = getattr(r, "score", 0)

        payload = r.payload or {}
        text = payload.get("text", "")
        source = payload.get("source", "")

        print(f"SCORE: {score}")
        print(text[:200])
        print("-" * 50)

        # IMPORTANT: DO NOT over-filter
        if text and len(text.strip()) > 30:
            contexts.append(text)

        if source:
            sources.add(source)

    # -----------------------------
    # GUARANTEED FALLBACK
    # -----------------------------
    if len(contexts) == 0:

        print("⚠️ No good matches → fallback triggered")

        for r in results[:3]:
            payload = r.payload or {}
            text = payload.get("text", "")

            if text:
                contexts.append(text)

    return {
        "contexts": contexts,
        "sources": list(sources)
    }