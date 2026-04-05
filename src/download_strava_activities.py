import pandas as pd
from datetime import datetime

from src.config import ACTIVITY_TYPE_BLACKLIST
from src.utils import list_activity_csv_files


def get_already_read_files(data_path):
    return list_activity_csv_files(data_path)


def last_activity_date(files):
    dates_str = [d.split("__")[-1].split(".")[0] for d in files]
    dates = [datetime.strptime(d, "%Y%m%d") for d in dates_str]
    last_date = max(dates)

    return last_date


def download_strava_activities(client, data_path):
    read_files = get_already_read_files(data_path)
    last_date = last_activity_date(read_files)

    print(f"Reading Activities After: {last_date} \n")
    activities = client.get_activities(after=last_date)

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
