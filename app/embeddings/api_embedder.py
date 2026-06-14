from sentence_transformers import SentenceTransformer
import numpy as np

_embedder = None

# =================================

# LOAD MODEL ONCE

# =================================

def get_embedder():

 global _embedder

 if _embedder is None:

    _embedder = SentenceTransformer(
        "sentence-transformers/BAAI/bge-small-en-v1.5"
    )

 return _embedder

# =================================

# SAFE TEXT CLEANER

# =================================

def sanitize_text(x):


# already string
 if isinstance(x, str):
    return x

# nested list -> flatten
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

 # single string
 if isinstance(texts, str):
    texts = [texts]

# bulletproof cleaning
 cleaned_texts = [

    sanitize_text(t)

    for t in texts

    if t is not None
]

 print("🔥 CLEANED TYPES:")

 for t in cleaned_texts[:3]:

    print(type(t), t[:80])

 model = get_embedder()

 vectors = model.encode(
    cleaned_texts,

    normalize_embeddings=True,

    convert_to_numpy=True)
 return vectors.tolist()
