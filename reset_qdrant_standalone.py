
from qdrant_client import QdrantClient

# 🔥 PUT YOUR VALUES DIRECTLY HERE (NO IMPORTS)
QDRANT_URL = "https://7baacd1f-4d38-4707-af6f-a4084e562e52.sa-east-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDU1YWFjOGYtZDE1MC00ZDNhLTkwMDUtZjcwZTIwMGE2NmYzIn0.bsARLw7YW4xaXAJX85WK2E_iIsrN7NFUl5CY9DwZWmw"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)

collections = client.get_collections()

print("Found collections:", [c.name for c in collections.collections])

for c in collections.collections:
    print(f"🗑 Deleting: {c.name}")
    client.delete_collection(c.name)

print("✅ DONE: All collections deleted")
