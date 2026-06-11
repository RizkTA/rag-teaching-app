def expand_query(query):

    q = query.lower()

    expansions = [query]

    if "recursive array" in q:
        expansions.extend([
            "recursion apip install rank-bm25rray traversal",
            "recursive array printing",
            "print array recursively in cpp",
            "recursive function array"
        ])

    if "pointer" in q:
        expansions.extend([
            "memory address",
            "pointer arithmetic",
            "cpp pointers"
        ])

    return " ".join(expansions)