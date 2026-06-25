import fitz  # PyMuPDF



MAX_CHUNKS = 50
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150



def ingest_pdf(file_path):

    chunks = extract_pdf_chunks(file_path)

    return {
        "file": file_path,
        "type": "pdf",
        "chunks": chunks
    }


def chunk_text(text):
    print("CHUNK_SIZE =", CHUNK_SIZE)
    print("CHUNK_OVERLAP =", CHUNK_OVERLAP)
    if CHUNK_OVERLAP >= CHUNK_SIZE:
            raise ValueError(
                f"Invalid chunk settings: "
                f"CHUNK_SIZE={CHUNK_SIZE}, "
                f"CHUNK_OVERLAP={CHUNK_OVERLAP}"
            )

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

        all_chunks = []

        with fitz.open(pdf_path) as doc:

            print("PDF PAGES:", len(doc))

            for page_num in range(len(doc)):

                page = doc[page_num]

                try:
                    text = page.get_text("text")
                except Exception as e:
                    print("PAGE READ ERROR:", e)
                    continue

                if not text or not text.strip():
                    continue

                page_chunks = chunk_text(text)

                for chunk in page_chunks:

                    all_chunks.append(chunk)

                    if len(all_chunks) >= MAX_CHUNKS:

                        print("⚠️ MAX CHUNKS REACHED")

                        return all_chunks

        print("TOTAL CHUNKS:", len(all_chunks))

        return all_chunks

    except Exception as e:

        print("PDF INGEST ERROR:", e)

        return []