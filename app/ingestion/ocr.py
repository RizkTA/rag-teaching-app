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
        "--force-ocr",
        pdf_path,
        output_pdf
    ]

    print("RUNNING:")
    print(" ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print("RETURN CODE:", result.returncode)

    print("STDOUT:")
    print(result.stdout)

    print("STDERR:")
    print(result.stderr)

    result.check_returncode()

    print("✅ OCR COMPLETE")

    return output_pdf