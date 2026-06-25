import os
import subprocess


def run_ocr(pdf_path: str) -> str:

    print("=" * 80)
    print("🔥 STARTING OCR")
    print("=" * 80)

    output_pdf = pdf_path.replace(
        ".pdf",
        "_ocr.pdf"
    )

    cmd = [
        "ocrmypdf",
        "--skip-text",
        "--force-ocr",
        pdf_path,
        output_pdf
    ]

    print("RUNNING:")
    print(" ".join(cmd))

    subprocess.run(
        cmd,
        check=True
    )

    print("✅ OCR COMPLETE")

    return output_pdf