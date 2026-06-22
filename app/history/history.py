import os
import pandas as pd
from datetime import datetime

UPLOAD_HISTORY_FILE = "upload_history.csv"
def load_history():

    print(
        "READING:",
        os.path.abspath(
            UPLOAD_HISTORY_FILE
        )
    )

    if os.path.exists(
            UPLOAD_HISTORY_FILE
    ):

        try:

            df = pd.read_csv(
                UPLOAD_HISTORY_FILE
            )

            for col in [
                "date",
                "time",
                "filename",
                "status",
                "chunks",
                "file_hash"
            ]:

                if col not in df.columns:
                    df[col] = ""

            return df

        except Exception as e:

            print(
                "❌ HISTORY READ ERROR:",
                e
            )

    return pd.DataFrame(
        columns=[
            "date",
            "time",
            "filename",
            "status",
            "chunks",
            "file_hash"
        ]
    )

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

    print(
        "✅ HISTORY SAVED"
    )

    print(
        os.path.abspath(
            UPLOAD_HISTORY_FILE
        )
    )