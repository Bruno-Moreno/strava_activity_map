from dotenv import load_dotenv

from src.strava_connection import strava_connection
from src.download_strava_activities import download_strava_activities
from src.read_activities_data import get_activities_data
from src.dash_app import StravaActivitiesApp  

data_path = "data" 
favicon = "favicon.ico"

def launch(new_activities):

    if new_activities == "y":
        print("Reading New Activities")
        client = strava_connection()
        download_strava_activities(client, data_path)

    df = get_activities_data(data_path)
    strava_app = StravaActivitiesApp(df, favicon)
    strava_app.create_app() 
    strava_app.run()


if __name__ == '__main__':
    
    load_dotenv() 
    new_activities = input("Read new activities? (y/n): ")
    launch(new_activities)
