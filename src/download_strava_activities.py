from datetime import datetime, timedelta, timezone

import pandas as pd

from src.config import ACTIVITY_TYPE_BLACKLIST
from src.strava_listing import list_activities


def download_strava_activities(client, data_path, days: int) -> None:
    after = datetime.now(timezone.utc) - timedelta(days=days)

    print(f"Reading Activities After: {after.isoformat()} \n")
    activities = list_activities(client, after=after)

    for a in activities:
        id = a.id
        activity_name = a.name
        activity_type = a.type.root
        start_date_date = a.start_date
        start_date_str = start_date_date.strftime("%Y%m%d")
        distance = f"{float(a.distance) / 1000:.2f}K"

        csv_name = f"{activity_name}__{start_date_str}.csv"

        if activity_type not in ACTIVITY_TYPE_BLACKLIST:
            activity = client.get_activity_streams(id, types=["latlng", "altitude"])

            try:
                latlng = activity["latlng"].data
                altitude = activity["altitude"].data
                data_ = pd.DataFrame([*latlng], columns=["lat", "lon"])
                data_["altitude"] = altitude
                data_["distance"] = distance
                data_["activity_id"] = id
                data_["activity_name"] = activity_name
                data_["activity_type"] = activity_type
                data_.to_csv(f"{data_path}//{csv_name}", index=False)
                print(f"Activity: {activity_name} saved successfully")
            except KeyError:
                print(f"Activity {activity_name} doesn't have gps data")
