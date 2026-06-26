import gc
import fitz
import pytesseract
from PIL import Image

from app.ingestion.ingest import mem


def ocr_pdf(pdf_path: str) -> str:

    print("=" * 80)
    print("🔥 LIGHT OCR")
    print("=" * 80)

    doc = fitz.open(pdf_path)

    all_text = []

    print("TOTAL PAGES:", len(doc))
    for page_num in range(len(doc)):

        print(f"OCR PAGE {page_num + 1}/{len(doc)}")

        page = doc.load_page(page_num)

        # ---------------------------------------
        # Try normal text extraction first
        # ---------------------------------------
        text = page.get_text().strip()

        if text:
            print(f"Page {page_num + 1}: text found")
            all_text.append(text)
            continue

        print(f"Page {page_num + 1}: running OCR")
# ---------------------------------------
# OCR only if needed
# ---------------------------------------
        # Much smaller than 300 dpi
        mem(f"After pixmap {page_num}")
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )
        mem(f"After OCR {page_num}")
        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        page_text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )
        mem(f"After OCR {page_num}")
        all_text.append(page_text)

        image.close()

        del image
        del pix
        del page

        gc.collect()

    doc.close()

    return "\n".join(all_text)