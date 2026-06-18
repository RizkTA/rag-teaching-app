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

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def extract_pdf_chunks(pdf_path):

    print("PDF OPEN")

    try:

        doc = fitz.open(pdf_path)

        print("PDF PAGES:", len(doc))

        all_chunks = []

        for page_num in range(len(doc)):

            print("READING PAGE", page_num + 1)

            page = doc[page_num]

            try:
                text = page.get_text("text")
            except Exception as e:
                print("PAGE READ ERROR:", e)
                continue

            if not text or not text.strip():
                continue

            print("PAGE CHARS:", len(text))

            page_chunks = chunk_text(text)

            all_chunks.extend(page_chunks)

            print("CURRENT CHUNKS:", len(all_chunks))

            if len(all_chunks) >= MAX_CHUNKS:

                print("⚠️ MAX CHUNKS REACHED")

                all_chunks = all_chunks[:MAX_CHUNKS]

                break

        doc.close()

        print("TOTAL CHUNKS:", len(all_chunks))

        return all_chunks

    except Exception as e:

        print("PDF INGEST ERROR:", e)

        return []