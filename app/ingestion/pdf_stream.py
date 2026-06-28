import gc
import fitz
import pytesseract
import psutil

from PIL import Image

from app.jobs import update_job


# ==========================================================
# Memory helper
# ==========================================================

def memory_mb():

    return round(

        psutil.Process().memory_info().rss
        / 1024 / 1024,

        1

    )


# ==========================================================
# Stream PDF pages
# ==========================================================

def stream_pdf_pages(path: str, job_id=None):
    """
    Streams one page at a time.

    Returns

        page_number
        page_text
        total_pages

    Memory usage stays nearly constant.
    """

    print("=" * 80)
    print("📖 STREAMING PDF")
    print("=" * 80)

    doc = fitz.open(path)

    total_pages = len(doc)

    print("TOTAL PAGES:", total_pages)

    for page_number in range(total_pages):

        page = doc.load_page(page_number)

        text = page.get_text("text").strip()

        # ---------------------------------------------
        # OCR if needed
        # ---------------------------------------------

        if len(text.split()) < 10:

            print(f"🔍 OCR page {page_number + 1}")

            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                alpha=False
            )

            image = Image.frombytes(

                "RGB",

                [pix.width, pix.height],

                pix.samples

            )

            text = pytesseract.image_to_string(

                image,

                config="--psm 6"

            ).strip()

            image.close()

            del image
            del pix

        # ---------------------------------------------
        # Update progress
        # ---------------------------------------------

        if job_id:

            progress = int(

                (page_number + 1)

                / total_pages

                * 35

            )

            update_job(

                job_id,

                stage=f"📖 Reading page {page_number+1}/{total_pages}",

                pages=page_number + 1,

                total_pages=total_pages,

                progress=min(progress, 35),

                memory=memory_mb()

            )

        yield (

            page_number + 1,

            text,

            total_pages

        )

        # ---------------------------------------------
        # Free memory
        # ---------------------------------------------

        del page
        del text

        gc.collect()

        try:

            import ctypes

            ctypes.CDLL("libc.so.6").malloc_trim(0)

        except Exception:

            pass

    doc.close()

    gc.collect()

    print("=" * 80)
    print("✅ PDF COMPLETE")
    print("=" * 80)