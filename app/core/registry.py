store = None
embedder = None

def get_store():
    global store
    if store is None:
        from app.ingestion.ingest import store as s
        store = s
    return store


def get_embedder():
    global embedder
    if embedder is None:
        from app.embeddings.local_embedder import LocalEmbedder
        embedder = LocalEmbedder()
    return embedder