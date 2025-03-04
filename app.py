from src.activities_data import get_activities_data
from src.dash_app import StravaActivitiesApp 

data_path = "data" 
favicon = "favicon.ico"
google_drive_folder_id = '1DQuDISsUud2YvNMTNuQbu7JI7xgBewD_'

def launch():

    df = get_activities_data(google_drive_folder_id)
    strava_app = StravaActivitiesApp(df, favicon)
    strava_app.create_app() 
    strava_app.run()


if __name__ == '__main__':
    
    launch()
