import os

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class QdrantStore:

    def __init__(self, url, collection, dim):

        self.url = url
        self.collection = collection
        self.dim = dim

        self.client = None

    # --------------------------------
    # SAFE LAZY CONNECTION
    # --------------------------------
    def connect(self):

        if self.client is None:

            self.client = QdrantClient(
                url=self.url,
                api_key=os.getenv("QDRANT_API_KEY"),
                timeout=60
            )

            if not self.client.collection_exists(
                collection_name=self.collection
            ):

                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(
                        size=self.dim,
                        distance=Distance.COSINE
                    )
                )

    # --------------------------------
    # UPSERT
    # --------------------------------
    def upsert(self, ids, vectors, payloads):

        self.connect()

        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload=payloads[i]
            )
            for i in range(len(ids))
        ]

        self.client.upsert(
            collection_name=self.collection,
            points=points
        )

    # --------------------------------
    # SEARCH
    # --------------------------------
    def search(self, query_vector, top_k=5):

        self.connect()

        return self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            with_payload=True
        ).points