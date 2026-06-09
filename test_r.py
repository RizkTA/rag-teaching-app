
from app.ingestion.ingest import store, embedder

query = "what is data science"

vec = embedder.embed([query])[0]

result = store.search(vec)

print(result)