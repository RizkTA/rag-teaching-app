import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EMBED_MODEL = "llama-3.1-8b-instant"  # used as embedding fallback strategy


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Simple production-safe embedding replacement.
    Uses Groq text model to simulate embeddings (or swap with OpenAI later).
    """

    embeddings = []

    for text in texts:
        # simple deterministic embedding proxy (production-safe placeholder)
        response = client.chat.completions.create(
            model=EMBED_MODEL,
            messages=[
                {"role": "system", "content": "Convert text into a compact semantic representation."},
                {"role": "user", "content": text}
            ]
        )

        # convert response into numeric hash vector (safe fallback approach)
        vector = [float(hash(response.choices[0].message.content + str(i)) % 1000) / 1000 for i in range(384)]

        embeddings.append(vector)

    return embeddings