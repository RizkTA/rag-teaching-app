from app.embeddings.local_embedder import LocalEmbedder
from app.vectorstores.qdrant_store import QdrantStore
from app.config import *

embedder = LocalEmbedder(EMBED_MODEL)

store = QdrantStore(QDRANT_URL, QDRANT_COLLECTION, EMBED_DIM)


def retrieve_context(question, top_k=5):

    query_vector = embedder.embed([question])[0]

    results = store.search(query_vector, top_k=top_k)

    contexts = []

    for r in results:

        payload = r.payload or {}

        text = payload.get("text", "")

        if text:
            contexts.append(text)

    return "\n\n".join(contexts)