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
@lru_cache(maxsize=1)
def get_embedder():

    print("🔥 ENTER get_embedder")

    from sentence_transformers import SentenceTransformer

    print("🔥 AFTER SENTENCE_TRANSFORMER IMPORT")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    print("🔥 MODEL LOADED")

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

    return [[0.0] * 384 for _ in texts]
print("🔥 EMBEDDER.PY IMPORT END")