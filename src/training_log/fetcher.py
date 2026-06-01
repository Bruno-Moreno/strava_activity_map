import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from stravalib import Client

from src.config import TRAINING_LOG_PATH, TRAINING_LOG_WHITELIST
from src.strava_listing import list_activities
from src.training_log.store import TRAINING_LOG_COLUMNS, upsert_training_log


def _build_metadata(activity) -> str:
    md: dict[str, float] = {}
    calories = getattr(activity, "calories", None)
    if calories:
        md["calories"] = float(calories)
    if activity.distance is not None:
        md["distance_km"] = round(float(activity.distance) / 1000, 2)
    if activity.average_speed is not None:
        speed_ms = float(activity.average_speed)
        if speed_ms > 0:
            if activity.sport_type.root in {"Run", "Swim"}:
                md["avg_pace_min_per_km"] = round((1000 / speed_ms) / 60, 2)
            else:
                md["avg_speed_kmh"] = round(speed_ms * 3.6, 2)
    return json.dumps(md)


def _duration_seconds(activity) -> int:
    moving_time = activity.moving_time
    if hasattr(moving_time, "total_seconds"):
        return int(moving_time.total_seconds())
    return int(moving_time)


def fetch_training_log(
    client: Client,
    days: int = 7,
    log_path: str = TRAINING_LOG_PATH,
) -> pd.DataFrame:
    after = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"Fetching training log since {after.isoformat()}")

    rows = []
    for a in list_activities(client, after=after, sport_types=TRAINING_LOG_WHITELIST):
        rows.append(
            {
                "activity_id": a.id,
                "timestamp": a.start_date.isoformat(),
                "activity_type": a.sport_type.root,
                "duration_seconds": _duration_seconds(a),
                "metadata": _build_metadata(a),
            }
        )

    new_df = pd.DataFrame(rows, columns=TRAINING_LOG_COLUMNS)
    print(f"Fetched {len(new_df)} training-log rows from Strava")
    return upsert_training_log(log_path, new_df)
