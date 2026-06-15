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

    chunk_size = 500
    overlap = 100

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks