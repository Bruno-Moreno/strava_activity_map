import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input


class StravaActivitiesApp:
    def __init__(self, activities, favicon):
        self.activities = activities
        self.app = Dash()
        self.app._favicon = favicon

    def create_app(self):
        self.app.layout = [
            html.H1(children="Strava Activities", style={"textAlign": "center"}),
            dcc.Dropdown(
                id="dropdown-multi-selection",
                options=list(self.activities.activity_name_and_date.unique())
                + ["Select All"],
                value=["Select All"],
                multi=True,
            ),
            dcc.Graph(id="graph-content"),
        ]

        @callback(
            Output("graph-content", "figure"),
            Input("dropdown-multi-selection", "value"),
        )
        def update_graph(activity):
            if "Select All" in activity:
                df_loc = self.activities.copy()
            else:
                df_loc = self.activities[
                    self.activities.activity_name_and_date.isin(activity)
                ].copy()

            fig = px.scatter_mapbox(
                df_loc,
                lat="lat",
                lon="long",
                hover_name="activity_name",
                hover_data=["date", "distance"],
                zoom=8.5,
                color="activity_type",
                center={"lat": -33.55, "lon": -70.60},
                width=1800,
                height=800,
            )
            fig.update_layout(
                mapbox_style="open-street-map",
                legend_title="Activity Type",
            )

            return fig

    def run(self):
        self.app.run(debug=False)
