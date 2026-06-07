from threading import Thread
from app.ingestion.ingest import ingest_pdf

def async_ingest(file_path: str):

    def run():
        ingest_pdf(file_path)

    Thread(target=run).start()