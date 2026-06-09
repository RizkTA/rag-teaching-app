import uuid


def ingest_txt(file_path: str):
    """
    Read plain text file and chunk it
    """

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "file": file_path,
        "type": "txt",
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
            "source": "txt",
            "language": "auto",
            "metadata": {
                "type": "text"
            }
        })

    return chunks