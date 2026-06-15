from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    PayloadSchemaType,
    Filter,
    FieldCondition,
    MatchValue
)

from app.config import QDRANT_API_KEY


# =========================================
# CREATE INDEXES
# =========================================
def ensure_indexes(client, collection_name):

    try:

        client.create_payload_index(
            collection_name=collection_name,

            field_name="metadata.file_hash",

            field_schema=PayloadSchemaType.KEYWORD
        )

        print("✅ file_hash index created")

    except Exception as e:

        print("⚠️ index may already exist:", e)


# =========================================
# QDRANT STORE
# =========================================
class QdrantStore:

    def __init__(self, url, collection_name, embed_dim):

        self.collection_name = collection_name
        self.embed_dim = embed_dim

        self.client = QdrantClient(
            url=url,
            api_key=QDRANT_API_KEY,
            timeout=120
        )

        # create collection if needed
        self._ensure_collection()

        # create indexes
        ensure_indexes(
            self.client,
            self.collection_name
        )

    # =====================================
    # CREATE COLLECTION
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

            print("✅ Collection created")

        else:
            print("✅ Collection already exists")

    # =====================================
    # UPSERT
    # =====================================
    def upsert(self, ids, vectors, payloads, batch_size=32):

        for i in range(0, len(ids), batch_size):

            points = [

                PointStruct(
                    id=ids[j],
                    vector=vectors[j],
                    payload=payloads[j]
                )

                for j in range(
                    i,
                    min(i + batch_size, len(ids))
                )
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

        print(f"✅ Upserted {len(ids)} chunks")

    # =====================================
    # SEARCH
    # =====================================
    def search(self, query_vector, top_k=5, language=None):

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

        return [

            {
                "id": getattr(r, "id", None),

                "score": float(
                    getattr(r, "score", 0.0)
                ),

                "payload": getattr(r, "payload", {}) or {}
            }

            for r in points
        ]

    # =====================================
    # FILE HASH EXISTS
    # =====================================
    def file_hash_exists(self, file_hash):

        records, _ = self.client.scroll(

            collection_name=self.collection_name,

            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.file_hash",
                        match=MatchValue(value=file_hash)
                    )
                ]
            ),

            limit=1,

            with_payload=True
        )

        return len(records) > 0
