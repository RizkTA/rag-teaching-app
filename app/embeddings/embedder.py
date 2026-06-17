import os
from functools import lru_cache

# =================================
# FORCE CPU ONLY (IMPORTANT FOR RENDER)
# =================================
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# =================================
# LOAD EMBEDDING MODEL ONCE
# =================================
from functools import lru_cache
print("🔥 EMBEDDER.PY IMPORT START")

from functools import lru_cache
@lru_cache(maxsize=1)
def get_embedder():

    print("STEP D")

    from sentence_transformers import SentenceTransformer

    print("STEP E")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    print("STEP F")

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

    print("STEP A")

    from sentence_transformers import SentenceTransformer

    print("STEP B")

    import psutil
    import os

    process = psutil.Process(os.getpid())

    print(
        "MEMORY BEFORE MODEL:",
        process.memory_info().rss / 1024 / 1024,
        "MB"
    )

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    print("STEP C")

    print(
        "MEMORY AFTER MODEL:",
        process.memory_info().rss / 1024 / 1024,
        "MB"
    )

    return [[0.0] * 384 for _ in texts]