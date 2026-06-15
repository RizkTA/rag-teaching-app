import uuid


def ingest_md(file_path: str):
    """
    Read markdown file and chunk it
    """

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "file": file_path,
        "type": "md",
        "chunks": chunk_text(text)
    }


def chunk_text(text, chunk_size=800):

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(words[i:i + chunk_size])

        chunks.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": "md",
            "language": "auto",
            "metadata": {
                "type": "markdown"
            }
        })

    return chunks