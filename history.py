from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_HISTORY_FILE = str(
    BASE_DIR / "upload_history.csv"
)