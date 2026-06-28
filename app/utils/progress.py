import threading
import uuid

_jobs = {}

_lock = threading.Lock()


def create_job(filename):

    job_id = str(uuid.uuid4())

    with _lock:

        _jobs[job_id] = {

            "filename": filename,

            "progress": 0,

            "stage": "Queued",

            "status": "running"

        }

    return job_id


def update_job(
        job_id,
        progress=None,
        stage=None,
        status=None
):

    with _lock:

        if job_id not in _jobs:
            return

        if progress is not None:
            _jobs[job_id]["progress"] = progress

        if stage is not None:
            _jobs[job_id]["stage"] = stage

        if status is not None:
            _jobs[job_id]["status"] = status


def finish_job(job_id):

    update_job(
        job_id,
        progress=100,
        stage="Completed",
        status="completed"
    )


def fail_job(job_id, message):

    update_job(
        job_id,
        progress=100,
        stage=message,
        status="failed"
    )


def get_job(job_id):

    return _jobs.get(job_id)