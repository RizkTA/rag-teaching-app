from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType
import os
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

client.create_payload_index(
    collection_name=QDRANT_COLLECTION,
    field_name="file_hash",
    field_schema=PayloadSchemaType.KEYWORD
)

print("✅ file_hash index created successfully")