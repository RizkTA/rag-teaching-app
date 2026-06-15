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

# =========================================
# IMPORT CONFIG
# =========================================
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

        print("⚠️ Index may already exist:", e)


# =========================================
# QDRANT STORE
# =========================================
class QdrantStore:

    def __init__(
        self,
        url,
        collection_name,
        embed_dim
    ):

        self.collection_name = collection_name
        self.embed_dim = embed_dim

        print("🔥 CONNECTING TO QDRANT")
        print("🔥 URL:", url)
        print("🔥 API KEY EXISTS:", bool(QDRANT_API_KEY))

        self.client = QdrantClient(
            url=url,
            api_key=QDRANT_API_KEY,
            timeout=120
        )

        self._ensure_collection()

        ensure_indexes(
            self.client,
            self.collection_name
        )

    # =========================================
    # CREATE COLLECTION IF MISSING
    # =========================================
    def _ensure_collection(self):

        collections = self.client.get_collections()

        existing = [
            c.name
            for c in collections.collections
        ]

        if self.collection_name not in existing:

            print("🔥 Creating collection")

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embed_dim,
                    distance=Distance.COSINE
                )
            )

            print("✅ Collection created")

    # =========================================
    # UPSERT
    # =========================================
    def upsert(
        self,
        ids,
        vectors,
        payloads,
        batch_size=32
    ):

        for i in range(0, len(ids), batch_size):

            points = []

            for j in range(
                i,
                min(i + batch_size, len(ids))
            ):

                points.append(
                    PointStruct(
                        id=ids[j],
                        vector=vectors[j],
                        payload=payloads[j]
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

        print("✅ Upsert completed")

    # =========================================
    # SEARCH
    # =========================================
    def search(
        self,
        query_vector,
        top_k=5,
        language=None
    ):

        query_filter = None

        if language:

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="language",
                        match=MatchValue(
                            value=language
                        )
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

        parsed = []

        for r in points:

            parsed.append({

                "id":
                    getattr(r, "id", None),

                "score":
                    float(getattr(r, "score", 0.0)),

                "payload":
                    getattr(r, "payload", {}) or {}
            })

        return parsed
