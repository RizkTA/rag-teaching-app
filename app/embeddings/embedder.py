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

@lru_cache(maxsize=1)
def get_embedder():

    print("🔥 ENTER get_embedder")

    from sentence_transformers import SentenceTransformer

    print("🔥 BEFORE MODEL LOAD")

    #model = SentenceTransformer(
    #    "sentence-transformers/all-MiniLM-L6-v2",
    #    device="cpu"    )
    print("🔥 MODEL LOAD SKIPPED")
    return None
    #print("🔥 AFTER MODEL LOAD")

    #return model

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

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    print("STEP C")

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    print("STEP D")

    return vectors.tolist()