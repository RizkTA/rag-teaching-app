import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.ingestion.ingest import ingest_pdf, DATA_DIR


class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        if filepath.lower().endswith(".pdf"):
            print(f"\n📥 NEW PDF DETECTED: {filepath}")
            print("⚙️ Auto-ingesting...")

            try:
                result = ingest_pdf(filepath)
                print("✅ AUTO-INGEST COMPLETE:", result)

            except Exception as e:
                print("❌ AUTO-INGEST FAILED:", e)


def start_watcher():
    event_handler = PDFHandler()
    observer = Observer()

    observer.schedule(event_handler, str(DATA_DIR), recursive=False)

    observer.start()

    print(f"\n👀 WATCHING FOLDER: {DATA_DIR}")
    print("🚀 Auto-ingest is ACTIVE (drop PDFs here)")

    try:
        while True:
            time.sleep(2)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()