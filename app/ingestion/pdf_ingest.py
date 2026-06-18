import fitz  # PyMuPDF

MAX_CHUNKS = 500
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def ingest_pdf(file_path):

    chunks = extract_pdf_chunks(file_path)

    return {
        "file": file_path,
        "type": "pdf",
        "chunks": chunks
    }




def chunk_text(text):

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunks.append(text[start:end])

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def extract_pdf_chunks(pdf_path):

    print("PDF OPEN")

    doc = fitz.open(pdf_path)

    print("PDF PAGES:", len(doc))

    all_chunks = []

    for page_num in range(len(doc)):

        print("READING PAGE", page_num)

        page = doc[page_num]

        text = page.get_text()

        print("PAGE CHARS:", len(text))

        page_chunks = chunk_text(text)

        all_chunks.extend(page_chunks)

        if len(all_chunks) >= MAX_CHUNKS:

            print("⚠️ MAX CHUNKS REACHED")

            all_chunks = all_chunks[:MAX_CHUNKS]

            break

    print("TOTAL CHUNKS:", len(all_chunks))

    return all_chunks