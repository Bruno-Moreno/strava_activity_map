from pathlib import Path

import pandas as pd

TRAINING_LOG_COLUMNS = [
    "activity_id",
    "timestamp",
    "activity_type",
    "duration_seconds",
    "metadata",
]


def load_training_log(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame(columns=TRAINING_LOG_COLUMNS)
    return pd.read_csv(p)


def upsert_training_log(path: str | Path, new_rows: pd.DataFrame) -> pd.DataFrame:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = load_training_log(p)
    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined = combined.drop_duplicates(subset=["activity_id"], keep="last")
    combined = combined.sort_values("timestamp", ascending=False).reset_index(drop=True)
    combined.to_csv(p, index=False)
    return combined
