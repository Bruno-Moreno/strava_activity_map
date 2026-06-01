import os
import re

_ACTIVITY_FILENAME_RE = re.compile(r"^.+__\d{8}\.csv$")


def list_activity_csv_files(data_path: str) -> list[str]:
    """Return only files matching the per-activity pattern `{name}__{YYYYMMDD}.csv`.

    Other CSVs in `data_path` (e.g. exports, stray training-log files) are
    ignored so they don't break the date-parsing pipeline.
    """
    return [
        f
        for f in os.listdir(data_path)
        if os.path.isfile(os.path.join(data_path, f)) and _ACTIVITY_FILENAME_RE.match(f)
    ]
