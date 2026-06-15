from qdrant_client import QdrantClient
from app.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)

collection_name = QDRANT_COLLECTION


print(f"🗑 Deleting collection: {collection_name}")

client.delete_collection(
    collection_name=collection_name
)

print("✅ Done")
