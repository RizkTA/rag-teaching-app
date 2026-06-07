def rerank(results, query):

    query_words = set(query.lower().split())

    def score(r):
        text_words = set(r["text"].lower().split())
        overlap = len(query_words.intersection(text_words))
        return r["score"] + overlap

    return sorted(results, key=score, reverse=True)