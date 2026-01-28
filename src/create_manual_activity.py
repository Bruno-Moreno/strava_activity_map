import numpy as np
import pandas as pd
from datetime import datetime


def create_circle_around_point(lat, long, radius):
    n_datapoints = 100
    radians = np.linspace(0, 2 * np.pi, n_datapoints)

    lat_points = [lat + radius * np.cos(i) for i in radians]
    long_points = [long + radius * np.sin(i) for i in radians]

    return lat_points, long_points


if __name__ == "__main__":
    data_path = "data"

    # MADRID 40.417362, -3.701326
    lat = float(input("Enter the center latitude: "))
    long = float(input("Enter the center longitude: "))
    altitude = 24.2
    distance = "1.00K"
    activity_id = int(str(lat).replace(".", ""))
    activity_name = input("Enter the activity name: ")
    activity_type = "Walk"
    date_string_input = input("Enter the activity date: ")
    date_string_format = datetime.strptime(date_string_input, "%Y-%m-%d").strftime(
        "%Y%m%d"
    )
    csv_name = f"{activity_name}__{date_string_format}.csv"

    lat_points, long_points = create_circle_around_point(lat, long, radius=0.001)

    data = pd.DataFrame()
    data["lat"] = lat_points
    data["long"] = long_points
    data["altitude"] = altitude
    data["distance"] = distance
    data["activity_name"] = activity_name
    data["activity_type"] = activity_type
    data.to_csv(f"{data_path}//{csv_name}", index=False)

    print(f"Manual activity saved to {data_path}//{csv_name}")
