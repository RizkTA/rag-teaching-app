from app.embeddings.local_embedder import LocalEmbedder
from app.vectorstores.qdrant_store import QdrantStore
from app.config import *

embedder = LocalEmbedder(EMBED_MODEL)

store = QdrantStore(
    QDRANT_URL,
    QDRANT_COLLECTION,
    EMBED_DIM
)

query = "What is thyroid hormone?"

query_vector = embedder.embed([query])[0]

results = store.search(query_vector)

print("\n🔍 SEARCH RESULTS:\n")

for r in results:

    print("SCORE:", r.score)
    print("TEXT:")
    print(r.payload["text"][:500])
    print("\n-------------------\n")