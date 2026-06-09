from rank_bm25 import BM25Okapi

documents = []
bm25 = None


def build_bm25(chunks):

    global documents
    global bm25

    documents = chunks

    tokenized = [
        doc.lower().split()
        for doc in documents
    ]

    bm25 = BM25Okapi(tokenized)


def search_bm25(query, top_k=5):

    global bm25
    global documents

    if bm25 is None:
        return []

    scores = bm25.get_scores(
        query.lower().split()
    )

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]
