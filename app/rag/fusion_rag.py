from rank_bm25 import BM25Okapi
from app.embeddings.embedder import embed_texts
from app.vectorstores.store_provider import get_store
import numpy as np
import re

# =================================
# CLEAN TEXT
# =================================
def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# =================================
# CODE DETECTOR
# =================================
def detect_code(text):

    keywords = [
        "include",
        "cout",
        "printf",
        "def ",
        "class ",
        "{",
        "}",
        ";"
    ]

    return any(k in text for k in keywords)

# =================================
# REMOVE DUPLICATES
# =================================
def deduplicate(results):

    seen = set()

    unique = []

    for r in results:

        text = r["text"][:200]

        if text in seen:
            continue

        seen.add(text)

        unique.append(r)

    return unique

# =================================
# MAIN FUSION SEARCH
# =================================
def fusion_search(query):

    store = get_store()

    # =========================
    # EMBEDDING
    # =========================
    query_vector = embed_texts([query])[0]

    # =========================
    # VECTOR SEARCH
    # =========================
    vector_results = store.search(
        query_vector,
        top_k=15
    )
    print("VECTOR RESULTS:", len(vector_results))

    for r in vector_results:
        print(r)
    if not vector_results:
        return []

    docs = []

    # =========================
    # PARSE RESULTS
    # =========================
    for r in vector_results:

        payload = r.get("payload", {})

        text = payload.get("text", "")

        #source = r.get("source", "").lower()
        #source_boost = 0
        #if query.lower() in source: source_boost += 0.15
        if not text:
            continue

        score = float(r.get("score", 0))
        print(
            f"SCORE={score:.3f}",
            payload.get("filename"),
        )
        # HARD FILTER
        if score < 0.70:
            continue

        docs.append({

            "text": clean_text(text),

            "score": score,

            "source":
                payload.get("source", "unknown"),

            "filename":
                payload.get("filename", "unknown"),

            "chunk_id":
                payload.get("chunk_id", -1),

            "is_code":
                detect_code(text)
        })
    # =========================
    # BM25
    # =========================


    # =========================
    # BM25
    # =========================
    tokenized = [

        d["text"].split()

        for d in docs

        if d["text"].strip()
    ]

    # NOTHING LEFT
    if len(tokenized) == 0:
        return []

    bm25 = BM25Okapi(tokenized)

    bm25_scores = bm25.get_scores(
        query.split()
    )

    # =========================
    # FUSION SCORING
    # =========================
    for i, d in enumerate(docs):

        semantic_score = d["score"]

        keyword_score = float(
            bm25_scores[i]
        )

        code_boost = 0.15 if d["is_code"] else 0

        query_words = set(
            query.lower().split()
        )

        text_lower = d["text"].lower()

        keyword_hits = sum(
            1
            for w in query_words
            if w in text_lower
        )

        keyword_boost = keyword_hits * 0.20

        d["final_score"] = (
                semantic_score * 0.60 +
                keyword_score * 0.20 +
                keyword_boost +
                code_boost
        )

      #  d["final_score"] += source_boost

    # =========================
    # SORT
    # =========================
    docs.sort(
        key=lambda x:
            x["final_score"],
        reverse=True
    )
    if not docs:
        return []

    top_score = docs[0]["final_score"]

    print(
        "TOP SCORE:",
        top_score
    )
    if not docs:
        return []

    top_score = docs[0]["final_score"]

    print(
        "TOP SCORE:",
        top_score
    )
    docs = [

        d for d in docs

        if d["score"] >= 0.70
    ]
    # =========================
    # REMOVE DUPLICATES
    # =========================
    docs = deduplicate(docs)

    # =========================
    # DYNAMIC TOP K
    # =========================


    # NO RESULTS AFTER FILTERING
    if not docs:
        return []


    best_score = docs[0]["final_score"]

    filtered = [

        d for d in docs

        if d["final_score"] >= best_score * 0.85
    ]
    print("\nTOP RESULTS")

    for d in docs[:10]:
        print(
            d["score"],
            d["final_score"],
            d.get("filename")
        )
    return filtered[:3]
