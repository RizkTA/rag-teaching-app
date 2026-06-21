import os
import traceback
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
    print("GET EMBEDDER")
    print(type(_EMBEDDER))
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
    print("ENTER embed_texts")
    traceback.print_stack(limit=5)
    print("ENTER embed_texts")

    model = get_embedder()

    print("MODEL LOADED")

    all_vectors = []

    BATCH_SIZE = 4

    for i in range(0, len(texts), BATCH_SIZE):

        batch = texts[i:i+BATCH_SIZE]

        print(f"Embedding batch {i//BATCH_SIZE+1}")
        print("Batch size =", len(batch))

        print("BEFORE model.embed")

        batch_vectors = list(model.embed(batch))

        print("AFTER model.embed")

        all_vectors.extend(batch_vectors)

    print("EXIT embed_texts")

    return [v.tolist() for v in all_vectors]

print("🔥 EMBEDDER.PY IMPORT END")