import pandas as pd
import reverse_geocoder

from src.utils import list_activity_csv_files


def append_all_activities(data_path):
    data_files = list_activity_csv_files(data_path)
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


def mark_longest_activity_per_type(df):
    df["numerical_distance"] = df["distance"].str.replace("K", "").astype(float)
    df["longest_activity"] = df["numerical_distance"] == df.groupby("activity_type")[
        "numerical_distance"
    ].transform("max")
    df.drop(columns=["numerical_distance"], inplace=True)

    return df


def _sample_one_point_per_activity(df):
    return df.groupby("activity_name_and_date", as_index=False).first()[
        ["activity_name_and_date", "lat", "lon"]
    ]


def add_country_column(df):
    sample = _sample_one_point_per_activity(df)
    results = reverse_geocoder.search(list(zip(sample["lat"], sample["lon"])))
    sample["country"] = [r["cc"] for r in results]
    return df.merge(
        sample[["activity_name_and_date", "country"]],
        on="activity_name_and_date",
        how="left",
    )


def get_activities_data(data_path):
    df = append_all_activities(data_path)
    df = mark_longest_activity_per_type(df)
    df = add_country_column(df)

    print("Saving concated activities to: all_activities.csv")
    df.to_csv("all_activities.csv", index=False)

    return df
