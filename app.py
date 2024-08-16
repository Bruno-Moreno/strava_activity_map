# Libraries
# ----------------------------------------------------------------

import pandas as pd
import os 

import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input

# Data 
# ----------------------------------------------------------------

def iterate_over_routes(data_path):
    """Append all routes into a single dataframe"""

    data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f)) and f.endswith('csv')]
    df = pd.DataFrame() 
    for d in data_files:
        df_ = pd.read_csv(f'{data_path}//{d}')
        df_["date"] = d.split("__")[1].split(".")[0]
        df_["date"] = pd.to_datetime(df_["date"]).dt.date
        df_["activity_name_and_date"] = df_["activity_name"] + " " + df_["date"].astype(str)
        df = pd.concat([df, df_], axis = 0)
    
    return df 

data_path = "data" 
df = iterate_over_routes(data_path)

# App 
# ----------------------------------------------------------------

app = Dash()

app.layout = [
    html.H1(children='Strava Activities', style={'textAlign':'center'}),
    dcc.Dropdown(id='dropdown-multi-selection',
                 options = list(df.activity_name_and_date.unique()) + ["Select All"],
                 value = ["Select All"],
                 multi = True,
                ),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-multi-selection', 'value'), 
)

def update_graph(activity):

    if "Select All" in activity:
        df_loc = df.copy() 
    else:
        df_loc = df[df.activity_name_and_date.isin(activity)].copy()

    fig = px.scatter_mapbox(
        df_loc, 
        lat='lat', 
        lon='long',
        hover_name='activity_name',
        hover_data = ['date', 'distance'],
        zoom=8.5,
        color = 'activity_type',
        center={"lat": -33.55, "lon": -70.60},
        )
    fig.update_layout(
        mapbox_style="open-street-map",
        legend_title = "Activity Type",
        )

    return fig

if __name__ == '__main__':

    app.run(debug=True)