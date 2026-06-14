from functools import lru_cache


# =================================
# LOAD EMBEDDING MODEL ONCE
# =================================
@lru_cache(maxsize=1)
def get_embedder():

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        "BAAI/bge-small-en-v1.5"
    )


# =================================
# SAFE TEXT SANITIZER
# =================================
def sanitize_text(x):

    if x is None:
        return ""

    # already string
    if isinstance(x, str):
        return x

    # nested lists
    if isinstance(x, list):

        cleaned = []

        for item in x:

            if isinstance(item, list):
                cleaned.extend(
                    [str(v) for v in item]
                )

            else:
                cleaned.append(str(item))

        return " ".join(cleaned)

    # fallback
    return str(x)


# =================================
# EMBEDDING FUNCTION
# =================================
def embed_texts(texts):

    if isinstance(texts, str):
        texts = [texts]

    cleaned_texts = [
        sanitize_text(t)
        for t in texts
    ]

    if not cleaned_texts:
        return []

    model = get_embedder()

    vectors = model.encode(
        cleaned_texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return vectors.tolist()