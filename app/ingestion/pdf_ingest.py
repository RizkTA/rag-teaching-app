import fitz  # PyMuPDF
import uuid


def ingest_pdf(file_path: str):
    """
    Extract text from PDF and return chunks with metadata
    """

    doc = fitz.open(file_path)

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    # simple chunking
    chunks = chunk_text(text)

    return {
        "file": file_path,
        "type": "pdf",
        "chunks": chunks
    }


def chunk_text(text, chunk_size=800):
    """
    Simple safe chunker
    """

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])

        chunks.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "source": "pdf",
            "language": "auto",
            "metadata": {
                "type": "pdf"
            }
        })

    return chunks