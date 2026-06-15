from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION
)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

client.create_payload_index(
    collection_name=QDRANT_COLLECTION,
    field_name="file_hash",  # IMPORTANT
    field_schema=PayloadSchemaType.KEYWORD
)

print("✅ file_hash index created successfully")