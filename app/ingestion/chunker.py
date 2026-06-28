import gc

from app.jobs import update_job


# ==========================================================
# Return a list of chunks
# ==========================================================
def chunk_text(
    text,
    chunk_size=1200,
    overlap=250,
    job_id=None
):
    """
    Returns a list of chunks.
    """

    return list(
        stream_chunks(
            text,
            chunk_size,
            overlap,
            job_id
        )
    )


# ==========================================================
# Generator version
# ==========================================================
def stream_chunks(
    text,
    chunk_size=1200,
    overlap=250,
    job_id=None
):
    """
    Yields one chunk at a time.
    """

    if not text:
        return

    text = str(text).strip()

    if not text:
        return

    start = 0

    chunk_id = 0

    total_length = len(text)

    while start < total_length:

        end = min(
            start + chunk_size,
            total_length
        )

        chunk = text[start:end].strip()

        if chunk:

            chunk_id += 1


            yield chunk

        start += chunk_size - overlap

    gc.collect()