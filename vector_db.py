# vector_db.py

from typing import List, Dict
import numpy as np


try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install: pip install sentence-transformers")

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


class VectorDB:
    def __init__(self):
        self.texts: List[str] = []
        self.embeddings: np.ndarray = np.array([])

    def add_texts(self, texts: List[str]):
        """Add documents to the vector DB"""
        if not texts:
            return

        new_embeddings = model.encode(texts)

        if self.embeddings.size == 0:
            self.embeddings = np.array(new_embeddings)
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.texts.extend(texts)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Return top_k most similar texts"""
        if not query or len(self.texts) == 0:
            return []

        query_embedding = model.encode([query])

        sims = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = sims.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.texts[idx],
                "score": float(sims[idx])
            })

        return results

    def get_all_embeddings(self):
        """Return all embeddings + texts (for visualization)"""
        return self.embeddings, self.texts


# Singleton instance (important for FastAPI)
vector_db = VectorDB()