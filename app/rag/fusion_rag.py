from rank_bm25 import BM25Okapi
from app.embeddings.embedder import embed_texts
from app.vectorstores.store_provider import get_store
import numpy as np
import re
from app.rag.mmr import mmr_rerank
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
        time complexity definition
        algorithm complexity
        computational complexity
        asymptotic complexity
        asymptotic analysis
        running time
        growth rate
        efficiency of algorithms
        Big O notation
        Big O
        O(n)
        O(log n)
        O(n log n)
        O(n^2)
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
        top_k=40
    )
    print("VECTOR RESULTS:", len(vector_results))
    for r in vector_results:
        text = r["payload"]["text"].lower()

        if "time complexity" in text:
            print(r["score"])
            print(text[:500])
    for r in vector_results:
        print(r)
    count = 0

    for r in vector_results:

        text = r["payload"]["text"].lower()

        if "time complexity" in text:
            count += 1

    print("CHUNKS WITH TIME COMPLEXITY:", count)
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
        for d in docs[:10]:
            print(
                d["filename"],
                len(d["text"])
            )
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

    from app.rag.mmr import mmr_rerank

    docs = mmr_rerank(
        query,
        docs,
        top_k=20,
        lambda_param=0.7
    )
    # =================================
    # BM25
    # =================================

    import re

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

    query_tokens = [
        t
        for t in re.findall(r"\w+", query.lower())
        if t not in STOP_WORDS
    ]

    query_words = set(query_tokens)

    tokenized = [
        re.findall(r"\w+", d["text"].lower())
        for d in docs
    ]

    if not tokenized:
        return []

    bm25 = BM25Okapi(tokenized)

    bm25_scores = bm25.get_scores(query_tokens)

    for i, d in enumerate(docs):
        d["bm25_raw"] = float(bm25_scores[i])

    bm25_min = min(d["bm25_raw"] for d in docs)
    bm25_max = max(d["bm25_raw"] for d in docs)

    # =================================
    # OPTIONAL FILTER
    # =================================
    SPECIAL_PHRASES = [
        "time complexity",
        "dynamic programming",
        "segment tree",
        "binary search"
    ]

    phrase_docs = []

    for d in docs:
        text_lower = d["text"].lower()

        for p in SPECIAL_PHRASES:
            if p in query.lower() and p in text_lower:
                phrase_docs.append(d)
                break

    if phrase_docs:
        docs = phrase_docs

    filtered_docs = []

    for d in docs:

        text_lower = d["text"].lower()

        matches = sum(
            1
            for term in query_tokens
            if term in text_lower
        )

        if matches >= 1:
            filtered_docs.append(d)
    for d in docs:
        if "time complexity" in d["text"].lower():
            print(d["filename"])
            print(d["text"][:1000])
    if filtered_docs:
        docs = filtered_docs

    # =================================
    # RERANK
    # =================================

    for d in docs:

        text_lower = d["text"].lower()

        semantic_score = d["score"]
        if semantic_score < 0.60:
            continue

        # -----------------------------
        # BM25
        # -----------------------------

        if bm25_max > bm25_min:
            keyword_score = (
                                    d["bm25_raw"] - bm25_min
                            ) / (
                                    bm25_max - bm25_min
                            )
        else:
            keyword_score = 0

        # -----------------------------
        # COVERAGE
        # -----------------------------

        text_tokens = set(
            re.findall(r"\w+", text_lower)
        )

        matched_words = sum(
            1
            for w in query_words
            if w in text_tokens
        )

        coverage_score = matched_words / max(len(query_words), 1)

        # -----------------------------
        # BOOSTS
        # -----------------------------
        chunk_len = len(d["text"])

        if chunk_len > 1200:
            length_penalty = 0.85
        else:
            length_penalty = 1.0
        phrase_boost = 0
        extra_boost = 0
        if query.lower() in text_lower:
            phrase_boost +=  1.0
        if "dynamic programming" in query.lower():

            if "dynamic programming" in text_lower:
                phrase_boost += 0.4

            if "memoization" in text_lower:
                phrase_boost += 0.4


            if "tabulation" in text_lower:
                phrase_boost += 0.4

        if "time complexity" in query.lower():

            docs = [
                d for d in docs
                if (
                        "time complexity" in d["text"].lower()
                        or "big o" in d["text"].lower()
                        or "asymptotic" in d["text"].lower()
                )
            ]

            if "time complexity" in text_lower:
                extra_boost += 0.4


            if "complexity" in text_lower:
                extra_boost += 0.4

            if "running time" in text_lower:
                extra_boost += 0.4

            if "big o" in text_lower:
                extra_boost += 0.4
            if "asymptotic" in text_lower:
                extra_boost += 0.4

            if "o(" in text_lower:
                extra_boost += 0.4

        # -----------------------------
        # FILENAME BOOST
        # -----------------------------
        query_phrase = query.lower().strip()
        if query_phrase in text_lower:
            phrase_boost += 0.5

        filename = d["filename"].lower()



        # -----------------------------
        # CODE BONUS
        # -----------------------------

        code_boost = (
            0.05
            if d["is_code"]
            else 0
        )

        # -----------------------------
        # FINAL SCORE
        # -----------------------------

        d["final_score"] = (
                semantic_score * 0.70 +
                keyword_score * 0.30 +
                phrase_boost +
                extra_boost
        )

        if keyword_score < 0.05:
            d["final_score"] *= 0.5

        d["final_score"] *= length_penalty
        d["coverage_score"] = coverage_score
        d["keyword_score"] = keyword_score
        d["matched_words"] = matched_words
        print(
            d["filename"],
            "SEM=", semantic_score,
            "BM25=", keyword_score,
            "COV=", coverage_score,
            "PHRASE=", phrase_boost,
            "FINAL=", d["final_score"]
        )
    # =================================
    # SORT
    # =================================
    docs.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    docs = deduplicate(docs)
    docs = docs[:20]
    chunk_embeddings = embed_texts(
        [d["text"] for d in docs]
    )

    for d, emb in zip(docs, chunk_embeddings):
        d["embedding"] = emb
    print("\n===== BEFORE MMR =====")

    for d in docs[:20]:
        print(
            d["filename"],
            d["score"],
            d["text"][:150]
        )
    docs = mmr_rerank(
        query=query,
        docs=docs,
        top_k=10
    )


    return docs[:10]

