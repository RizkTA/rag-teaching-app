from datetime import datetime

import os
import pandas as pd
# app/history.py

import uuid
from datetime import datetime


from app.ingestion.ingest import get_store
import pandas as pd
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)
from qdrant_client.models import PointStruct
def delete_uploaded_file(file_hash):

    store = get_store()

    # delete vectors / embeddings if needed
    store.delete_by_file_hash(file_hash)

    # delete metadata record
    store.client.delete(
        collection_name="uploaded_files",
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="file_hash",
                    match=MatchValue(value=file_hash)
                )
            ]
        )
    )
def get_uploaded_files():

    store = get_store()

    records, _ = store.client.scroll(
        collection_name="uploaded_files",
        limit=10000,
        with_payload=True,
        with_vectors=False
    )

    rows = []

    for r in records:

        p = r.payload or {}

        rows.append({
            "filename": p.get("filename", ""),
            "file_hash": p.get("file_hash", ""),
            "chunks": p.get("chunks", 0),
            "date": p.get("date", ""),
            "time": p.get("time", ""),
            "status": p.get("status", "")
        })

    return pd.DataFrame(rows)
def save_uploaded_file(filename, file_hash, chunks, status="uploaded"):

    store = get_store()

    now = datetime.now()

    store.client.upsert(
        collection_name="uploaded_files",
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=[0.0],  # dummy vector (OK since this is metadata-only)
                payload={
                    "filename": filename,
                    "file_hash": file_hash,
                    "chunks": chunks,
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "status": status
                }
            )
        ]
    )

UPLOAD_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "upload_history.csv")





def save_history(
        filename,
        status="uploaded",
        filetype="",
        chunks=0,
        file_hash=""
):

    row = {

        "date":
            datetime.now().strftime("%Y-%m-%d"),

        "time":
            datetime.now().strftime("%H:%M:%S"),

        "filename":
            filename,

        "type":
            filetype,

        "status":
            status,

        "chunks":
            chunks,

        "file_hash":
            file_hash
    }

    columns = [

        "date",
        "time",
        "filename",
        "type",
        "status",
        "chunks",
        "file_hash"
    ]

    if os.path.exists(UPLOAD_HISTORY_FILE):

        df = pd.read_csv(
            UPLOAD_HISTORY_FILE
        )

    else:

        df = pd.DataFrame(
            columns=columns
        )

    df = pd.concat(
        [df, pd.DataFrame([row])],
        ignore_index=True
    )

    df.to_csv(
        UPLOAD_HISTORY_FILE,
        index=False
    )
    print("WRITING:", os.path.abspath(UPLOAD_HISTORY_FILE))
    print(
        "✅ HISTORY SAVED"
    )

    print(
        os.path.abspath(
            UPLOAD_HISTORY_FILE
        )
    )
def load_history():

    print(
        "READING:",
        os.path.abspath(
            UPLOAD_HISTORY_FILE
        )
    )
    #print("READING:", os.path.abspath(UPLOAD_HISTORY_FILE))
    columns = [
        "date",
        "time",
        "filename",
        "type",
        "status",
        "chunks",
        "file_hash"
    ]

    if os.path.exists(
        UPLOAD_HISTORY_FILE
    ):

        try:

            df = pd.read_csv(
                UPLOAD_HISTORY_FILE
            )

            print(
                "ROWS READ:",
                len(df)
            )

            print(
                "CSV COLUMNS:",
                list(df.columns)
            )

            # Add missing columns
            for col in columns:

                if col not in df.columns:

                    df[col] = ""

            # Reorder columns
            df = df[columns]

            return df

        except Exception as e:

            print(
                "❌ HISTORY READ ERROR:",
                e
            )

    else:

        print(
            "⚠ History file does not exist"
        )

    return pd.DataFrame(
        columns=columns
    )