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
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PayloadSchemaType
)

from app.config import QDRANT_API_KEY

from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

def delete_by_filename(
    self,
    filename
):

    self.client.delete(

        collection_name=self.collection_name,

        points_selector=Filter(

            must=[

                FieldCondition(

                    key="filename",

                    match=MatchValue(
                        value=filename
                    )
                )
            ]
        )
    )

    print(
        "✅ Deleted:",
        filename
    )
# =========================================
# CREATE INDEXES
# =========================================
def ensure_indexes(client, collection_name):

    try:

        client.create_payload_index(
            collection_name=collection_name,
            field_name="file_hash",
            field_schema=PayloadSchemaType.KEYWORD
        )

        print("✅ file_hash index ready")

    except Exception as e:

        print("⚠️ Index may already exist:", e)


# =========================================
# QDRANT STORE
# =========================================
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    VectorParams,
    Distance,
    PayloadSchemaType,
)

UPLOADED_FILES_COLLECTION = "uploaded_files"


class QdrantStore:
    def ensure_indexes(
            self,
            collection_name
    ):

        indexes = [

            ("file_hash", PayloadSchemaType.KEYWORD),

            ("filename", PayloadSchemaType.KEYWORD),

            ("status", PayloadSchemaType.KEYWORD),

            ("date", PayloadSchemaType.KEYWORD),
        ]

        for field_name, schema in indexes:

            try:

                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema
                )

                print(f"✅ Index created: {field_name}")

            except Exception:

                print(f"ℹ️ Index already exists: {field_name}")
    def _ensure_collection(
            self,
            collection_name,
            vector_size
    ):

        collections = self.client.get_collections()

        existing = {
            c.name
            for c in collections.collections
        }

        if collection_name in existing:
            print(f"✅ Collection '{collection_name}' already exists")
            return

        print(f"🔥 Creating collection '{collection_name}'")

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        print(f"✅ Collection '{collection_name}' created")
    def __init__(self, url, collection_name, embed_dim):

        print("=" * 70)
        print("🔥 CONNECTING TO QDRANT")
        print("URL:", url)
        print("API KEY EXISTS:", bool(QDRANT_API_KEY))
        print("=" * 70)

        self.collection_name = collection_name
        self.embed_dim = embed_dim

        try:

            self.client = QdrantClient(
                url=url,
                api_key=QDRANT_API_KEY,
                timeout=120,
            )

            # Verify connection immediately
            self.client.get_collections()

            print("✅ Connected to Qdrant")

        except ResponseHandlingException as e:

            print("❌ Could not connect to Qdrant")
            print(e)
            raise

        # Ensure collections exist
        self._ensure_collection(
            self.collection_name,
            self.embed_dim
        )

        self._ensure_collection(
            UPLOADED_FILES_COLLECTION,
            1
        )

        # Create payload indexes
        self.ensure_indexes(self.collection_name)
        self.ensure_indexes(UPLOADED_FILES_COLLECTION)

    def delete_by_file_hash(self, file_hash):

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="file_hash",
                        match=MatchValue(
                            value=file_hash
                        )
                    )
                ]
            ),
            wait=True
        )

        print(
            f"✅ Deleted vectors for hash: {file_hash}"
        )

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
            query_filter=query_filter,
            with_payload=True,
            with_vectors=True
        )

        points = getattr(results, "points", []) or []

        parsed = []

        for r in points:
            parsed.append({
                "id": r.id,
                "score": float(r.score),
                "payload": r.payload,
                "vector": r.vector
            })

        return parsed
    # =========================================
    # DELETE ENTIRE COLLECTION
    # =========================================
    def delete_all(self):

        self.client.delete_collection(
            collection_name=self.collection_name
        )

        print("✅ Collection deleted")

        # recreate empty collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embed_dim,
                distance=Distance.COSINE
            )
        )

        print("✅ Empty collection recreated")
