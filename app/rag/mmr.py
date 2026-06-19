# app/rag/mmr.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def mmr_rerank(
    docs,
    lambda_param=0.7,
    top_k=5
):
    """
    docs = [
        {
            "text": "...",
            "final_score": ...
        }
    ]
    """

    if not docs:
        return []

    if len(docs) <= top_k:
        return docs

    texts = [
        d["text"]
        for d in docs
    ]

    tfidf = TfidfVectorizer(
        stop_words="english"
    )

    matrix = tfidf.fit_transform(texts)

    sim_matrix = cosine_similarity(matrix)

    selected = [0]

    candidates = list(
        range(1, len(docs))
    )

    while (
        len(selected) < top_k
        and candidates
    ):

        best_idx = None
        best_score = -999

        for idx in candidates:

            relevance = docs[idx].get(
                "final_score",
                0
            )

            diversity = max(
                sim_matrix[idx][s]
                for s in selected
            )

            mmr_score = (
                lambda_param * relevance
                -
                (1 - lambda_param)
                * diversity
            )

            if mmr_score > best_score:

                best_score = mmr_score
                best_idx = idx

        selected.append(best_idx)

        candidates.remove(best_idx)

    return [
        docs[i]
        for i in selected
    ]