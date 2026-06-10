from sentence_transformers import SentenceTransformer

# ==============================
# LOAD MODEL ONCE
# ==============================
embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
    return embedder

# ==============================
# EMBED TEXTS
# ==============================
def embed_texts(texts):

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()