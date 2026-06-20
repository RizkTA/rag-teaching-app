import numpy as np


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b) +
        1e-9
    )


def apply_mmr(
    docs,
    top_k=5,
    lambda_param=0.75
):

    if len(docs) <= top_k:
        return docs

    selected = [docs[0]]

    remaining = docs[1:]

    while remaining and len(selected) < top_k:

        best_doc = None
        best_score = -999

        for candidate in remaining:

            relevance = candidate["final_score"]

            diversity = max(

                cosine_similarity(
                    candidate["embedding"],
                    s["embedding"]
                )

                for s in selected
            )

            mmr_score = (
                lambda_param * relevance
                -
                (1 - lambda_param) * diversity
            )

            if mmr_score > best_score:

                best_score = mmr_score
                best_doc = candidate

        selected.append(best_doc)
        remaining.remove(best_doc)

    return selected