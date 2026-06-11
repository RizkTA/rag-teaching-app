from qdrant_client import QdrantClient
from qdrant_client.models import (
VectorParams,
Distance,
PointStruct,
Filter,
FieldCondition,
MatchValue
)

from app.config import QDRANT_API_KEY

class QdrantStore:
 def __init__(
    self,
    url,
    collection_name,
    embed_dim
):

    self.collection_name = collection_name
    self.embed_dim = embed_dim

    self.client = QdrantClient(
        url=url,
        api_key=QDRANT_API_KEY,
        timeout=120
    )

    print("✅ Qdrant connected")

    self._ensure_collection()

# =====================================
# CREATE COLLECTION IF NOT EXISTS
# =====================================
def _ensure_collection(self):

    collections = self.client.get_collections()

    existing = [
        c.name
        for c in collections.collections
    ]

    if self.collection_name not in existing:

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embed_dim,
                distance=Distance.COSINE
            )
        )

        print(
            f"✅ Created collection: "
            f"{self.collection_name}"
        )

# =====================================
# UPSERT VECTORS
# =====================================
def upsert(
    self,
    ids,
    vectors,
    payloads,
    batch_size=32
):

    total = len(ids)

    for start in range(0, total, batch_size):

        end = min(start + batch_size, total)

        points = []

        for i in range(start, end):

            points.append(
                PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payloads[i]
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        print(
            f"✅ Upserted "
            f"{len(points)} vectors"
        )

# =====================================
# SEARCH
# =====================================
def search(self, query_vector, top_k=5, language=None):

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    query_filter = None

    if language:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="language",
                    match=MatchValue(value=language)
                )
            ]
        )

    results = self.client.query_points(
        collection_name=self.collection_name,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter
    )

    points = getattr(results, "points", []) or []

    # 🔥 IMPORTANT: normalize once here
    return [
        {
            "id": getattr(r, "id", None),
            "score": float(getattr(r, "score", 0.0)),
            "payload": getattr(r, "payload", {}) or {}
        }
        for r in points
        if getattr(r, "score", 0.0) > 0
    ]