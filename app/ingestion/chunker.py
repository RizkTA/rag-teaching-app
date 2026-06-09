# app/ingestion/chunker.py

def is_code(text):

    code_patterns = [
        "#include",
        "cout <<",
        "cin >>",
        "int main(",
        "def ",
        "print(",
        "class ",
        "{",
        "};"
    ]

    for p in code_patterns:
        if p in text:
            return True

    return False


def chunk_text(text):

    # =========================
    # CODE CHUNKING
    # =========================
    if is_code(text):

        chunk_size = 400
        overlap = 50

    # =========================
    # THEORY / LECTURE NOTES
    # =========================
    else:

        chunk_size = 1200
        overlap = 150

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
