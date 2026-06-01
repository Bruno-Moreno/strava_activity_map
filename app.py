from dotenv import load_dotenv

from src.config import TRAINING_LOG_PATH
from src.dash_app import StravaActivitiesApp
from src.read_activities_data import get_activities_data
from src.training_log.store import load_training_log

DATA_PATH = "data"
FAVICON = "favicon.ico"


def main(debug: bool = False) -> None:
    load_dotenv()
    df = get_activities_data(DATA_PATH)
    training_log_df = load_training_log(TRAINING_LOG_PATH)
    strava_app = StravaActivitiesApp(df, training_log_df, FAVICON, debug=debug)
    strava_app.create_app()
    strava_app.run_app()


if __name__ == "__main__":
    main()
