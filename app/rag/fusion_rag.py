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
    # =========================
    # QUERY EXPANSION
    # =========================

    expanded_query = query

    q = query.lower()
    print("\nQUERY:", query)
    print("\nEXPANDED QUERY:", expanded_query)
    if "time complexity" in q:
        expanded_query += """
        Big O notation
        running time
        algorithm efficiency
        asymptotic complexity
        O(n)
        O(log n)
        """

    if "dynamic programming" in q:
        expanded_query += """
        DP memoization tabulation
        """

    if "segment tree" in q:
        expanded_query += """
        range query interval tree
        """

    # =========================
    # EMBEDDING
    # =========================

    query_vector = embed_texts(
        [expanded_query]
    )[0]

    # =========================
    # VECTOR SEARCH
    # =========================
    vector_results = store.search(
        query_vector,
        top_k=100
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
        text = r["payload"].get("text", "").lower()

        if "dynamic programming" in text:
            print(
                "FOUND DP",
                r["score"],
                r["payload"].get("filename")
            )
        payload = r.get("payload", {})

        text = payload.get("text", "")
        source = (
                payload.get("filename", "")
                + " "
                + payload.get("source", "")
        ).lower()

        source_boost = 0

        for term in query.lower().split():
            if term in source:
                source_boost += 0.05
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
       # if score < 0.40:
        #    continue

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

    # Replace everything from BM25 onwards with this

    # =========================

    # BM25

    # =========================

    tokenized = [
        d["text"].lower().split()
        for d in docs
        if d["text"].strip()
    ]

    if not tokenized:
        return []

    bm25 = BM25Okapi(tokenized)

    query_tokens = query.lower().split()

    bm25_scores = bm25.get_scores(query_tokens)

    bm25_min = min(bm25_scores)
    bm25_max = max(bm25_scores)

    # =========================

    # FUSION SCORING

    # =========================

    for i, d in enumerate(docs):


     semantic_score = d["score"]

    # normalize BM25
    if bm25_max > bm25_min:
        keyword_score = (
                                bm25_scores[i] - bm25_min
                        ) / (
                                bm25_max - bm25_min
                        )
    else:
        keyword_score = 0

    text_lower = d["text"].lower()

    # =====================
    # EXACT PHRASE BOOST
    # =====================

    phrase_boost = 0

    if query.lower() in text_lower:
        phrase_boost = 0.40

    # =====================
    # WORD COVERAGE
    # =====================

    query_words = set(query_tokens)

    matched_words = sum(
        1
        for w in query_words
        if w in text_lower
    )

    coverage_score = (
        matched_words / len(query_words)
        if query_words
        else 0
    )

    # =====================
    # CODE BONUS
    # =====================

    code_boost = 0.05 if d["is_code"] else 0

    # =====================
    # FINAL SCORE
    # =====================

    d["final_score"] = (
            semantic_score * 0.55 +
            keyword_score * 0.20 +
            coverage_score * 0.20 +
            phrase_boost +
            code_boost
    )


    # =========================

    # SORT

    # =========================

    docs.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    docs = deduplicate(docs)

    if not docs:
        return []

    best_score = docs[0]["final_score"]

    # tighter filter

    filtered = [
        d
        for d in docs
        if d["final_score"] >= best_score * 0.90
    ]

    print("\nTOP RESULTS")

    for d in docs[:10]:
        print(
            d["score"],
            d["final_score"],
            d["filename"]
        )

    return filtered[:5]
