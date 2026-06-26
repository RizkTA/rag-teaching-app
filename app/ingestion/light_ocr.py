import io
import gc

import fitz
import pytesseract

from PIL import Image


def ocr_pdf(pdf_path: str) -> str:
    """
    OCR every page of a scanned PDF.

    Returns extracted text.
    """

    print("=" * 80)
    print("🔥 LIGHT OCR")
    print("=" * 80)

    doc = fitz.open(pdf_path)

    all_text = []

    total_pages = len(doc)

    print("TOTAL PAGES:", total_pages)

    for page_num, page in enumerate(doc):

        print(f"OCR PAGE {page_num + 1}/{total_pages}")

        pix = page.get_pixmap(
            dpi=300,
            alpha=False
        )

        image = Image.open(
            io.BytesIO(
                pix.tobytes("png")
            )
        )

        page_text = pytesseract.image_to_string(image)

        all_text.append(page_text)

        del image
        del pix

        gc.collect()

    doc.close()

    print("OCR TEXT LENGTH:", len("".join(all_text)))

    return "\n".join(all_text)