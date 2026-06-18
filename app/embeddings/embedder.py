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

    print("🔥 embed_texts start")

    texts = [
        sanitize_text(x)
        for x in texts
    ]

    texts = [t for t in texts if t]

    if not texts:
        return []

    model = get_embedder()

    vectors = list(model.embed(texts))

    print(f"🔥 embeddings generated: {len(vectors)}")

    return [v.tolist() for v in vectors]


print("🔥 EMBEDDER.PY IMPORT END")