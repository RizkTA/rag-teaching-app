from sentence_transformers import SentenceTransformer

embedder = None

def get_embedder():

 global embedder

 if embedder is None:

    embedder = SentenceTransformer(
        "jinaai/jina-embeddings-v2-base-code"
    )

 return embedder

def embed_texts(texts):

 model = get_embedder()

 embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    show_progress_bar=False,
    batch_size=4
 )

 return embeddings.tolist()
