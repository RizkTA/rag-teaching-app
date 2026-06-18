import os
from functools import lru_cache

print("🔥 EMBEDDER.PY IMPORT START")

os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Import once at module load
from fastembed import TextEmbedding

print("🔥 Creating FastEmbed singleton...")

_EMBEDDER = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

print("🔥 FastEmbed singleton ready")


@lru_cache(maxsize=1)
def get_embedder():
    return _EMBEDDER


def sanitize_text(x):

    if x is None:
        return ""

    if isinstance(x, str):
        return x.strip()

    if isinstance(x, list):

        cleaned = []

        for item in x:

            if isinstance(item, list):
                cleaned.extend(
                    str(v) for v in item if v is not None
                )
            else:
                cleaned.append(str(item))

        return " ".join(cleaned).strip()

    return str(x).strip()

def embed_texts(texts):

    model = get_embedder()
    print("MODEL:", model)
    all_vectors = []

    BATCH_SIZE = 4

    for i in range(0, len(texts), BATCH_SIZE):

        batch = texts[i:i+BATCH_SIZE]

        print(
            f"🔥 embedding batch "
            f"{i//BATCH_SIZE+1}"
        )

        batch_vectors = list(
            model.embed(batch)
        )

        all_vectors.extend(
            batch_vectors
        )

    return [
        v.tolist()
        for v in all_vectors
    ]

print("🔥 EMBEDDER.PY IMPORT END")