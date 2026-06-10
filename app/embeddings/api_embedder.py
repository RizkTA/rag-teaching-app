from sentence_transformers import SentenceTransformer

# ==============================
# LOAD MODEL ONCE
# ==============================
model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)


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