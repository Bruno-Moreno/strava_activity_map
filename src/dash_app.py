import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dcc, callback, Output, Input


class StravaActivitiesApp:
    def __init__(self, activities, favicon):
        self.activities = activities
        self.app = Dash(external_stylesheets=[dbc.themes.COSMO])
        self.app.title = "Strava Activities"
        self.app._favicon = favicon
        load_figure_template("COSMO")

    def create_app(self):
        self.app.layout = [
            html.H1(children="Strava Activities", style={"textAlign": "center"}),
            dcc.Dropdown(
                id="dropdown-multi-selection",
                options=["Select All"]
                + list(self.activities["activity_name_and_date"].unique()),
                value=["Select All"],
                multi=True,
            ),
            dcc.DatePickerRange(
                id="date-picker",
                start_date=self.activities["date"].min(),
                end_date=self.activities["date"].max(),
                display_format="YYYY-MM-DD",
            ),
            dcc.Graph(id="graph-content"),
        ]

        @callback(
            Output("graph-content", "figure"),
            Input("dropdown-multi-selection", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
        )
        def update_graph(activity, start_date, end_date):
            filter_start_date = self.activities["date"].astype(str) >= start_date
            filter_end_date = self.activities["date"].astype(str) <= end_date
            filter_activities = (
                self.activities["activity_name_and_date"].isin(activity)
            ) | ("Select All" in activity)

            df = self.activities[
                filter_start_date & filter_end_date & filter_activities
            ].copy()

            fig = px.scatter_mapbox(
                df,
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
