from qdrant_client import QdrantClient
import os
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

        print(
            "⚠️ file_hash index already exists "
            f"or could not be created: {e}"
        )


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

        print("🔥 QDRANT INIT")
        print("🔥 COLLECTION:", collection_name)
        print("🔥 EMBED DIM:", embed_dim)

        self.client = QdrantClient(
            url=url,
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=120
        )
        print("🔥 QDRANT URL:", url)
        print("🔥 API KEY EXISTS:", bool(QDRANT_API_KEY))

        try:
            collections = self.client.get_collections()
            print("✅ Qdrant Connected")
            print(collections)

        except Exception as e:
            print("❌ QDRANT CONNECTION FAILED")
            print(str(e))
        self._ensure_collection()

        ensure_indexes(
            self.client,
            self.collection_name
        )

        self._verify_collection()

    # =====================================
    # VERIFY COLLECTION
    # =====================================
    def _verify_collection(self):

        try:

            info = self.client.get_collection(
                self.collection_name
            )

            vector_size = (
                info.config.params.vectors.size
            )

            print(
                "🔥 COLLECTION VECTOR SIZE:",
                vector_size
            )

            print(
                "🔥 EXPECTED VECTOR SIZE:",
                self.embed_dim
            )

            if vector_size != self.embed_dim:

                raise Exception(
                    f"Vector size mismatch. "
                    f"Collection={vector_size}, "
                    f"Expected={self.embed_dim}"
                )

        except Exception as e:

            print(
                "❌ COLLECTION VERIFICATION FAILED:",
                e
            )

            raise

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

            print(
                f"✅ Created collection: "
                f"{self.collection_name}"
            )

        else:

            print(
                f"✅ Collection exists: "
                f"{self.collection_name}"
            )

    # =====================================
    # UPSERT
    # =====================================
    def upsert(
        self,
        ids,
        vectors,
        payloads,
        batch_size=32
    ):

        if not ids:

            print("⚠️ No IDs supplied")

            return

        if not vectors:

            raise Exception(
                "No vectors supplied"
            )

        if len(ids) != len(vectors):

            raise Exception(
                f"ID/vector mismatch: "
                f"{len(ids)} vs {len(vectors)}"
            )

        if len(ids) != len(payloads):

            raise Exception(
                f"ID/payload mismatch: "
                f"{len(ids)} vs {len(payloads)}"
            )

        total = len(ids)

        print(
            f"🔥 UPSERTING {total} vectors"
        )

        for i in range(
            0,
            total,
            batch_size
        ):

            end = min(
                i + batch_size,
                total
            )

            points = [

                PointStruct(
                    id=ids[j],
                    vector=vectors[j],
                    payload=payloads[j]
                )

                for j in range(i, end)
            ]

            try:

                self.client.upsert(

                    collection_name=self.collection_name,

                    points=points,

                    wait=True
                )

            except Exception:

                import traceback

                print(
                    "❌ QDRANT UPSERT FAILED"
                )

                traceback.print_exc()

                raise

        print(
            f"✅ Upserted {total} chunks"
        )

    # =====================================
    # SEARCH
    # =====================================
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

        try:

            results = self.client.query_points(

                collection_name=self.collection_name,

                query=query_vector,

                limit=top_k,

                query_filter=query_filter
            )

            points = getattr(
                results,
                "points",
                []
            ) or []

            return [

                {
                    "id":
                        getattr(
                            p,
                            "id",
                            None
                        ),

                    "score":
                        float(
                            getattr(
                                p,
                                "score",
                                0.0
                            )
                        ),

                    "payload":
                        getattr(
                            p,
                            "payload",
                            {}
                        ) or {}
                }

                for p in points
            ]

        except Exception:

            import traceback

            print(
                "❌ SEARCH FAILED"
            )

            traceback.print_exc()

            return []

    # =====================================
    # FILE HASH EXISTS
    # =====================================
    def file_hash_exists(
        self,
        file_hash
    ):

        try:

            records, _ = self.client.scroll(

                collection_name=self.collection_name,

                scroll_filter=Filter(

                    must=[

                        FieldCondition(

                            key="file_hash",

                            match=MatchValue(
                                value=file_hash
                            )
                        )
                    ]
                ),

                limit=1,

                with_payload=False
            )

            exists = len(records) > 0

            print(
                f"🔥 DUPLICATE CHECK: "
                f"{exists}"
            )

            return exists

        except Exception as e:

            print(
                "❌ DUPLICATE CHECK FAILED:",
                e
            )

            return False