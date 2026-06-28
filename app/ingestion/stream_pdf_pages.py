import gc
import ctypes

import fitz
import pytesseract

from PIL import Image


def stream_pdf_pages(pdf_path):

    print("=" * 80)
    print("📖 STREAMING PDF")
    print("=" * 80)

    doc = fitz.open(pdf_path)

    try:

        for page_number in range(len(doc)):

            print(f"PAGE {page_number + 1}/{len(doc)}")

            page = doc.load_page(page_number)

            text = page.get_text("text").strip()

            if len(text.split()) > 10:

                yield text

            else:

                print("Running OCR...")

                pix = page.get_pixmap(
                    dpi=250,
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    (pix.width, pix.height),
                    pix.samples
                ).convert("L")

                text = pytesseract.image_to_string(

                    image,

                    config="--psm 6"

                )

                image.close()

                del image
                del pix

                yield text

            del page
            del text

            gc.collect()

            try:
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception:
                pass

    finally:

        doc.close()

        gc.collect()

        try:
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except Exception:
            pass

        print("PDF closed")