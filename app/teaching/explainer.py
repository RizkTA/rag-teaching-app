def explain_rag(query, retriever, generator):
    retrieved = retriever(query)

    explanation = {
        "question": query,
        "retrieved_chunks": retrieved["contexts"],
        "sources": retrieved["sources"],
    }

    answer = generator(query, retrieved["contexts"])
    explanation["final_answer"] = answer

    return explanation