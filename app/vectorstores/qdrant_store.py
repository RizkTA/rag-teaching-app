from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

from app.config import QDRANT_API_KEY


class QdrantStore:

    def __init__(
        self,
        url,
        collection,
        dim
    ):

        self.collection = collection

        # =========================
        # CONNECT CLIENT
        # =========================
        self.client = QdrantClient(
            url=url,
            api_key=QDRANT_API_KEY
        )

        print("✅ Qdrant connected")

        # =========================
        # CREATE COLLECTION
        # =========================
        collections = self.client.get_collections()

        existing = [
            c.name
            for c in collections.collections
        ]

        if collection not in existing:

            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(
                    size=dim,
                    distance=Distance.COSINE
                )
            )

            print(
                f"✅ Created collection: {collection}"
            )

    # =========================
    # UPSERT
    # =========================
    def upsert(
        self,
        ids,
        vectors,
        payloads
    ):

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
            collection_name=self.collection,
            points=points
        )

    # =========================
    # SEARCH
    # =========================
    def search(
        self,
        query_vector,
        top_k=5
    ):

        return self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k
        )
