from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

from app.config import QDRANT_API_KEY


class QdrantStore:

    def __init__(self, url, collection_name, embed_dim):

        self.collection_name = collection_name

        self.client = QdrantClient(
            url=url,
            api_key=QDRANT_API_KEY,
            timeout=60
        )

        print("✅ Qdrant connected")

        # =========================
        # CREATE COLLECTION IF MISSING
        # =========================
        collections = self.client.get_collections()

        existing = [
            c.name
            for c in collections.collections
        ]

        if collection_name not in existing:

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embed_dim,
                    distance=Distance.COSINE
                )
            )

            print(f"✅ Created collection: {collection_name}")

    # =========================
    # UPSERT
    # =========================
    def upsert(self, ids, vectors, payloads):

        points = []

        for i in range(len(ids)):

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

    # =========================
    # SEARCH
    # =========================
    def search(self, query_vector, top_k=5):

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        return results
