import pandas as pd 
import os 

def get_already_read_files(data_path):

    already_read_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f)) and f.endswith('csv')]

    return already_read_files 

def download_strava_activities(client, data_path):

    already_read_files = get_already_read_files(data_path)
    activities = client.get_activities(limit=100)

    for a in activities: 
        id = a.id
        activity_name = a.name
        activity_type = a.type.root
        start_date_date = a.start_date
        start_date_str = start_date_date.strftime("%Y%m%d")
        distance = f"{float(a.distance)/1000:.2f}K"

        csv_name = f"{activity_name}__{start_date_str}.csv" 
        print(f"Activity: {activity_name}, Type: {activity_type}")

        if (activity_type not in ["WeightTraining", "Workout", "VirtualRide", "Treadmill"]) and (csv_name not in already_read_files): 
            
            activity = client.get_activity_streams(id, types = ["latlng", "altitude"])

            try:
                latlng = activity["latlng"].data
                altitude = activity["altitude"].data
                data_ = pd.DataFrame([*latlng], columns=['lat','long'])
                data_['altitude'] = altitude
                data_["distance"] = distance
                data_['activity_id'] = id 
                data_['activity_name'] = activity_name        
                data_['activity_type'] = activity_type    
                data_.to_csv(f'{data_path}//{csv_name}', index = False)
            except KeyError:
                print("Activity doesn't have gps data")