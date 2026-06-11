import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# GROQ
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# QDRANT
# =========================
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

# embedding size (match your model!)
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))

# embedding model name
EMBED_MODEL = 768