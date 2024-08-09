# ------------------------------------------
# Libraries 

import pandas as pd
import os 

import plotly.express as px

# ------------------------------------------
# Globals 

data_path = "..//data" 
templates_path = "..//templates"

# ------------------------------------------
# Functions 
 
def iterate_over_routes(data_path):
    """Append all routes into a single dataframe"""

    data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f)) and f.endswith('csv')]
    df = pd.DataFrame() 
    for d in data_files:
        df_ = pd.read_csv(f'{data_path}//{d}')
        df = pd.concat([df, df_], axis = 0)

    return df 


if __name__ == "__main__":

    df = iterate_over_routes(data_path)

    fig = px.scatter_mapbox(
        df, 
        lat='lat', 
        lon='long',
        hover_name='activity_name',  # Assuming you have a column with run IDs
        zoom=10,
        color = 'activity_type'
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.write_html(f'{templates_path}//strava_activities.html')

