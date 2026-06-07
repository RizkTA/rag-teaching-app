def visualize_retrieval(query, retriever):
    results = retriever(query)

    return {
        "query": query,
        "top_chunks": [
            {"rank": i + 1, "text": c}
            for i, c in enumerate(results["contexts"])
        ]
    }