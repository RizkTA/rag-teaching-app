from qdrant_client import QdrantClient
from app.config import *

client = QdrantClient(url=QDRANT_URL)

client.delete_collection(
    collection_name=QDRANT_COLLECTION
)

print("✅ Qdrant collection deleted")