import os


def list_activity_csv_files(data_path: str) -> list[str]:
    return [
        f
        for f in os.listdir(data_path)
        if os.path.isfile(os.path.join(data_path, f)) and f.endswith("csv")
    ]
