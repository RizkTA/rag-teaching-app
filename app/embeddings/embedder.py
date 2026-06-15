import os
from functools import lru_cache

# =================================
# FORCE CPU ONLY (IMPORTANT FOR RENDER)
# =================================
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# =================================
# LOAD EMBEDDING MODEL ONCE
# =================================
@lru_cache(maxsize=1)
def get_embedder():

    from sentence_transformers import SentenceTransformer

    print("🔥 Loading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    print("✅ Embedding model loaded")

    return model


# =================================
# SAFE TEXT SANITIZER
# =================================
def sanitize_text(x):

    if x is None:
        return ""

    # already string
    if isinstance(x, str):
        return x.strip()

    # nested lists
    if isinstance(x, list):

        cleaned = []

        for item in x:

            if isinstance(item, list):

                cleaned.extend(
                    [str(v) for v in item if v is not None]
                )

            else:
                cleaned.append(str(item))

        return " ".join(cleaned).strip()

    # fallback
    return str(x).strip()


# =================================
# EMBEDDING FUNCTION
# =================================
def embed_texts(texts):

    # single string
    if isinstance(texts, str):
        texts = [texts]

    # sanitize
    cleaned_texts = [

        sanitize_text(t)

        for t in texts

        if t is not None
    ]

    # remove empty strings
    cleaned_texts = [
        t for t in cleaned_texts
        if t.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedder()

    vectors = model.encode(
        cleaned_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=16
    )
    print(
        "🔥 EMBEDDINGS SHAPE:",
        vectors.shape
    )
    return vectors.tolist()