import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# API KEYS
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# QDRANT
# =========================
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

# =========================
# EMBEDDINGS
# =========================
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))