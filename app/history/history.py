import os
import pandas as pd
from datetime import datetime

#UPLOAD_HISTORY_FILE = "upload_history.csv"
import os
import pandas as pd

UPLOAD_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "upload_history.csv"
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