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

from rank_bm25 import BM25Okapi

def build_bm25(docs):
    global BM25_INDEX, BM25_DOCS

    BM25_DOCS = docs

    tokenized_docs = [
        d["text"].split()
        for d in docs
    ]

    BM25_INDEX = BM25Okapi(tokenized_docs)

    print(
        "BM25 built with",
        len(docs),
        "documents"
    )
import numpy as np

def bm25_search(query, top_k=5):

    scores = BM25_INDEX.get_scores(query.split())

    idx = np.argsort(scores)[::-1][:top_k]

    return [BM25_DOCS[i] for i in idx]