import argparse

from dotenv import load_dotenv

from src.config import TRAINING_LOG_DEFAULT_DAYS
from src.download_strava_activities import download_strava_activities
from src.strava_connection import strava_connection
from src.training_log.fetcher import fetch_training_log

DATA_PATH = "data"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Strava data (GPS streams + training log)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=TRAINING_LOG_DEFAULT_DAYS,
        help=f"Days of training log to fetch (default {TRAINING_LOG_DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--skip-gps",
        action="store_true",
        help="Skip the GPS-stream download (only refresh the training log)",
    )
    parser.add_argument(
        "--skip-log",
        action="store_true",
        help="Skip the training log (only refresh GPS streams)",
    )
    args = parser.parse_args()

    load_dotenv()
    client = strava_connection()

    if not args.skip_gps:
        download_strava_activities(client, DATA_PATH, days=args.days)
    if not args.skip_log:
        fetch_training_log(client, days=args.days)


if __name__ == "__main__":
    main()
