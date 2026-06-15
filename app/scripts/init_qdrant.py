from qdrant_client import QdrantClient

from app.config import QDRANT_URL

client = QdrantClient(url=QDRANT_URL)

client.recreate_collection(
    collection_name="docs",
    vectors_config={
        "size": 384,
        "distance": "Cosine"
    }
)