import os
import pandas as pd


def get_activities_data(data_path):
    """Append all routes into a single dataframe"""

    data_files = [
        f
        for f in os.listdir(data_path)
        if os.path.isfile(os.path.join(data_path, f)) and f.endswith("csv")
    ]
    df = pd.DataFrame()
    for d in data_files:
        df_ = pd.read_csv(f"{data_path}//{d}")
        df_["date"] = d.split("__")[1].split(".")[0]
        df_["date"] = pd.to_datetime(df_["date"]).dt.date
        df_["activity_name_and_date"] = (
            df_["activity_name"] + " " + df_["date"].astype(str)
        )
        df = pd.concat([df, df_], axis=0)

    df.sort_values(by=["date"], ascending=False, inplace=True)

    return df
