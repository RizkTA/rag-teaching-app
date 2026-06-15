import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from qdrant_client import QdrantClient
from app.config import QDRANT_URL, QDRANT_API_KEY


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)


def reset_all():

    collections = client.get_collections()

    if not collections.collections:
        print("⚠️ No collections found")
        return

    for c in collections.collections:

        print(f"🗑 Deleting: {c.name}")

        client.delete_collection(c.name)

    print("✅ All Qdrant collections deleted successfully")


if __name__ == "__main__":
    reset_all()
