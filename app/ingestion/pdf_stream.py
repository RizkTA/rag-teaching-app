import gc
import fitz
import pytesseract

from PIL import Image


def stream_pdf_pages(path):

    """
    Yield one page of text at a time.

    If a page has selectable text,
    use it.

    Otherwise OCR only that page.
    """

    print("=" * 80)
    print("📖 STREAMING PDF")
    print("=" * 80)

    doc = fitz.open(path)

    total_pages = len(doc)

    print("TOTAL PAGES:", total_pages)

    for page_num in range(total_pages):

        print(f"PAGE {page_num + 1}/{total_pages}")

        page = doc.load_page(page_num)

        # -------------------------
        # Try normal PDF extraction
        # -------------------------

        text = page.get_text("text").strip()

        words = len(text.split())

        print("WORDS FOUND:", words)

        if words > 10:

            print("✅ Text extracted")

            yield text

        else:

            print("🔍 Running OCR")

            pix = page.get_pixmap(

                matrix=fitz.Matrix(1.5, 1.5),

                alpha=False
            )

            image = Image.frombytes(

                "RGB",

                [pix.width, pix.height],

                pix.samples
            )

            page_text = pytesseract.image_to_string(

                image,

                config="--psm 6"
            ).strip()

            yield page_text

            image.close()

            del image
            del pix

        del page
        del text

        gc.collect()

    doc.close()

    print("=" * 80)
    print("✅ PDF STREAM COMPLETE")
    print("=" * 80)