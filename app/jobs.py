from threading import Lock
import uuid
import time


# ==========================================================
# In-memory Job Store
# ==========================================================

_jobs = {}

_lock = Lock()


# ==========================================================
# Create Job
# ==========================================================

def create_job(filename: str) -> str:
    """
    Creates a new upload/ingestion job.

    Returns
    -------
    job_id : str
    """

    job_id = str(uuid.uuid4())

    with _lock:

        _jobs[job_id] = {

            "job_id": job_id,

            "filename": filename,

            "status": "running",

            "stage": "Initializing...",

            "progress": 0,

            "pages": 0,

            "total_pages": 0,

            "chunks": 0,

            "embedded": 0,

            "total_embeddings": 0,

            "memory": 0,

            "elapsed": 0,

            "message": "",

            "started": time.time(),

            "finished": None

        }

    return job_id


# ==========================================================
# Update Job
# ==========================================================

def update_job(job_id: str, **kwargs):
    """
    Updates any job field.

    Example
    -------
    update_job(
        job_id,
        progress=42,
        stage="Embedding..."
    )
    """

    with _lock:

        job = _jobs.get(job_id)

        if job is None:
            return

        job.update(kwargs)

        job["elapsed"] = round(

            time.time() - job["started"],

            1

        )


# ==========================================================
# Complete Job
# ==========================================================
def finish_job(
    job_id: str,
    success=True,
    message=""
):

    with _lock:

        job = _jobs.get(job_id)

        if job is None:
            return

        job["status"] = "completed" if success else "failed"

        job["progress"] = 100

        job["stage"] = (
            "Completed"
            if success
            else "Failed"
        )

        job["message"] = message

        job["finished"] = time.time()

        job["elapsed"] = round(
            job["finished"] - job["started"],
            1
        )

# ==========================================================
# Read Job
# ==========================================================

def get_job(job_id: str):

    with _lock:

        return _jobs.get(job_id)


# ==========================================================
# Delete Job
# ==========================================================

def delete_job(job_id: str):

    with _lock:

        if job_id in _jobs:

            del _jobs[job_id]


# ==========================================================
# List Jobs
# ==========================================================

def list_jobs():

    with _lock:

        return list(_jobs.values())