from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.config import QDRANT_API_KEY


class QdrantStore:

    def __init__(self, url, collection_name, embed_dim):

        self.collection_name = collection_name

        self.client = QdrantClient(
            url=url,
            api_key=QDRANT_API_KEY,
            timeout=60
        )

        self.embed_dim = embed_dim

        self._ensure_collection()

    def _ensure_collection(self):

        collections = self.client.get_collections()
        existing = [c.name for c in collections.collections]

        if self.collection_name not in existing:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embed_dim,
                    distance=Distance.COSINE
                )
            )

            print(f"✅ Created collection: {self.collection_name}")

    def upsert(self, ids, vectors, payloads, batch_size=64):

        for i in range(0, len(ids), batch_size):

            points = [
                PointStruct(
                    id=ids[j],
                    vector=vectors[j],
                    payload=payloads[j]
                )
                for j in range(i, min(i + batch_size, len(ids)))
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def search(self, query_vector, top_k=5, language=None):

        query_filter = None

        if language:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

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

        return results.points if hasattr(results, "points") else results
