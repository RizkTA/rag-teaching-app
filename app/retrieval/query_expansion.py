def expand_query(query):

    q = query.lower()

    expansions = [query]

    # =========================
    # RECURSION
    # =========================
    if "recursive array" in q:

        expansions.extend([
            "recursion in c++",
            "recursive array printing",
            "print array recursively",
            "recursive function array",
            "array recursion cpp"
        ])

    # =========================
    # POINTERS
    # =========================
    if "pointer" in q:

        expansions.extend([
            "pointer arithmetic",
            "memory address",
            "cpp pointers"
        ])

    return " ".join(expansions)