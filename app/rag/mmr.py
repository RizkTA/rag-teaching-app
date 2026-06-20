from app.embeddings.embedder import embed_texts
import numpy as np


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    denom = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denom == 0:
        return 0

    return np.dot(a, b) / denom

import numpy as np


def mmr_rerank(
    query,
    docs,
    top_k=10,
    lambda_param=0.7
):

    if not docs:
        return []

    # keep only docs that already have embeddings
    docs = [
        d
        for d in docs
        if d.get("embedding") is not None
    ]

    if not docs:
        return []

    # query embedding only
    query_embedding = embed_texts([query])[0]

    # use stored embeddings
    doc_embeddings = [
        d["embedding"]
        for d in docs
    ]

    selected = []
    selected_idx = []

    similarities = [
        cosine_similarity(
            query_embedding,
            emb
        )
        for emb in doc_embeddings
    ]

    first = int(np.argmax(similarities))

    selected.append(docs[first])
    selected_idx.append(first)

    while len(selected) < min(top_k, len(docs)):

        best_score = -999
        best_idx = None

        for i in range(len(docs)):

            if i in selected_idx:
                continue

            relevance = similarities[i]

            diversity = max(
                cosine_similarity(
                    doc_embeddings[i],
                    doc_embeddings[j]
                )
                for j in selected_idx
            )

            mmr_score = (
                lambda_param * relevance
                - (1 - lambda_param) * diversity
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        if best_idx is None:
            break

        selected.append(docs[best_idx])
        selected_idx.append(best_idx)

    return selected