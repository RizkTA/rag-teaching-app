from app.core.worker import celery_app
from app.ingestion.ingest import ingest_file


@celery_app.task(bind=True)
def process_file(self, path: str, filename: str):
    try:
        return ingest_file(path, filename)
    except Exception as e:
        return {"status": "failed", "error": str(e)}