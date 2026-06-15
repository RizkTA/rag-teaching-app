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

from rank_bm25 import BM25Okapi


def bm25_search(query, docs, top_k=5):

    tokenized_docs = [d["text"].split() for d in docs]

    bm25 = BM25Okapi(tokenized_docs)

    scores = bm25.get_scores(query.split())

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [x[0] for x in ranked[:top_k]]