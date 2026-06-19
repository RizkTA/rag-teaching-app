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
        dynamic programming
        DP
        memoization
        tabulation
        recurrence
        subproblem
        optimal substructure
        overlapping subproblems
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
        top_k=200
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

    # =========================
    # BM25
    # =========================

    tokenized = [
        re.findall(r"\w+", d["text"].lower())
        for d in docs
    ]

    if not tokenized:
        return []

    bm25 = BM25Okapi(tokenized)

    STOP_WORDS = {
        "what",
        "is",
        "the",
        "a",
        "an",
        "of",
        "to",
        "in",
        "for",
        "and"
    }

    # tokenize query exactly the same way
    query_tokens = [
        t
        for t in re.findall(r"\w+", query.lower())
        if t not in STOP_WORDS
    ]

    # BM25 uses the actual query
    bm25_scores = bm25.get_scores(query_tokens)

    bm25_min = float(min(bm25_scores))
    bm25_max = float(max(bm25_scores))

    important_terms = query_tokens

    filtered_docs = []

    for d in docs:

        text_lower = d["text"].lower()

        matches = sum(
            1 for term in important_terms
            if term in text_lower
        )

        if matches >= max(1, len(important_terms) // 2):
            filtered_docs.append(d)

    docs = filtered_docs if filtered_docs else docs
    # =========================
    import re
    query_tokens = re.findall(
        r"\w+",
        query.lower()
    )

    query_words = set(query_tokens)

    for i, d in enumerate(docs):

        semantic_score = d["score"]
        print("QUERY TOKENS:", query_tokens)
        print("BM25:", bm25_scores[:10])
        # BM25 normalization
        if bm25_max > bm25_min:
            keyword_score = (
                                    bm25_scores[i] - bm25_min
                            ) / (
                                    bm25_max - bm25_min
                            )
        else:
            keyword_score = 0

        text_lower = d["text"].lower()

        # Exact phrase boost
        #phrase_boost = 0.75 if query.lower() in text_lower else 0
        phrase_boost = 0

        important_phrases = [
            "dynamic programming",
            "time complexity",
            "segment tree",
            "binary search",
            "memoization",
        ]


        if "time complexity" in query.lower():

            if "complexity" in text_lower:
                d["final_score"] += 1.0

            if "running time" in text_lower:
                d["final_score"] += 1.0

            if "big o" in text_lower:
                d["final_score"] += 1.0

            if "o(" in text_lower:
                d["final_score"] += 1.0

        if "dynamic programming" in query.lower():
            if "dynamic programming" in text_lower:
                phrase_boost += 0.3

        if "time complexity" in query.lower():
            if "time complexity" in text_lower:
                phrase_boost += 0.3
        for phrase in important_phrases:
            if phrase in query.lower() and phrase in text_lower:
                phrase_boost += 0.30
        STOP_WORDS = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "of",
            "to",
            "in",
            "for",
            "and"
        }
        # Word coverage
        import re


        # Code bonus
        code_boost = 0.05 if d["is_code"] else 0
        filename_lower = d["filename"].lower()
        filename = d["filename"].lower()

        source_boost = 0

        if "complexity" in filename:
            source_boost += 0.20

        if "programming" in filename:
            source_boost += 0.15

        if "algorithm" in filename:
            source_boost += 0.15
        title_boost = 0

        for word in query_words:
            if word in filename_lower:
                title_boost += 0.2
        # =====================
        # WORD COVERAGE
        # =====================

        text_tokens = set(
            re.findall(r"\w+", text_lower)
        )

        matched_words = sum(
            1
            for w in query_words
            if w in text_tokens
        )

        coverage_score = (
            matched_words / len(query_words)
            if query_words
            else 0
        )
        code_boost = 0.05 if d["is_code"] else 0
        # =====================
        # FINAL SCORE
        # =====================

        d["final_score"] = (
                semantic_score * 0.30 +
                keyword_score * 0.50 +
                coverage_score * 0.20 +
                phrase_boost +
                code_boost +
                source_boost +
                title_boost
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
    for i, d in enumerate(docs[:20]):
        print(
            "\nFILE:", d["filename"],
            "\nSEM:", d["score"],
            "\nFINAL:", d["final_score"],
            "\nTEXT:", d["text"][:150]
        )
        print("QUERY:", query)
        print("TOKENS:", query_tokens)
        print("MATCHED:", matched_words)
        print("COVERAGE:", coverage_score)
        print("BM25:", bm25_scores[i])
        print("FINAL:", d["final_score"])
        print("TEXT:", d["text"][:150])
    return filtered[:5]
