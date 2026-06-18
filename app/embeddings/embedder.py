import os
from functools import lru_cache

print("🔥 EMBEDDER.PY IMPORT START")

os.environ["CUDA_VISIBLE_DEVICES"] = ""

@lru_cache(maxsize=1)
def get_embedder():

    print("🔥 Loading FastEmbed model...")

    from fastembed import TextEmbedding

    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    print("🔥 FastEmbed model loaded")

    return model


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
                    [str(v) for v in item if v is not None]
                )
            else:
                cleaned.append(str(item))

        return " ".join(cleaned).strip()

    return str(x).strip()

def embed_texts(texts):

    print("🔥 embed_texts start")

    model = get_embedder()

    texts = [str(x) for x in texts if str(x).strip()]

    if not texts:
        return []

    vectors = list(model.embed(texts))

    print("🔥 embeddings:", len(vectors))

    return [v.tolist() for v in vectors]


print("🔥 EMBEDDER.PY IMPORT END")