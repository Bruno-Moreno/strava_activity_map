import webbrowser
import plotly.express as px
import dash_bootstrap_components as dbc
from threading import Timer
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dcc, callback, Output, Input


class StravaActivitiesApp:
    def __init__(self, activities, favicon, debug, port="8050"):
        self.activities = activities
        self.app = Dash(external_stylesheets=[dbc.themes.COSMO])
        self.app.title = "Strava Activities"
        self.app._favicon = favicon
        self.port = port
        self.debug = debug
        load_figure_template("COSMO")

    def create_app(self):
        # Enhanced styling with better layout and visual appeal
        header_style = {
            "textAlign": "center",
            "color": "#2c3e50",
            "fontSize": "2.5rem",
            "fontWeight": "bold",
            "marginBottom": "2rem",
            "paddingTop": "1rem",
            "textShadow": "2px 2px 4px rgba(0,0,0,0.1)",
        }

        container_style = {
            "width": "100%",
            "margin": "0",
            "padding": "2rem",
            "backgroundColor": "#f8f9fa",
            "minHeight": "100vh",
        }

        card_style = {
            "backgroundColor": "white",
            "borderRadius": "12px",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
            "padding": "1.5rem",
            "marginBottom": "1.5rem",
            "border": "1px solid #e9ecef",
        }

        dropdown_style = {
            "paddingLeft": "20px",
            "paddingRight": "20px",
            "marginBottom": "1rem",
        }

        date_picker_style = {
            "paddingLeft": "20px",
            "paddingRight": "20px",
            "paddingTop": "10px",
            "marginBottom": "1rem",
        }

        checkbox_style = {
            "paddingLeft": "20px",
            "paddingRight": "20px",
            "paddingTop": "10px",
            "marginBottom": "1.5rem",
        }

        graph_style = {
            "borderRadius": "8px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "backgroundColor": "white",
            "width": "100%",
            "height": "100%",
            "overflow": "hidden",
        }

        self.app.layout = dbc.Container(
            [
                # Header
                html.Div(
                    [
                        html.H1(
                            children="🏃‍♂️ Strava Activities Map", style=header_style
                        ),
                        html.Hr(
                            style={"borderColor": "#dee2e6", "marginBottom": "2rem"}
                        ),
                    ]
                ),
                # Controls Card
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    "📊 Activity Filters",
                                    style={"margin": "0", "color": "#495057"},
                                )
                            ],
                            style={
                                "backgroundColor": "#e9ecef",
                                "borderRadius": "8px 8px 0 0",
                            },
                        ),
                        dbc.CardBody(
                            [
                                # Activity Selection
                                html.Div(
                                    [
                                        html.Label(
                                            "Select Activities:",
                                            style={
                                                "fontWeight": "bold",
                                                "marginBottom": "0.5rem",
                                                "color": "#495057",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="dropdown-multi-selection",
                                            options=["Select All"]
                                            + list(
                                                self.activities[
                                                    "activity_name_and_date"
                                                ].unique()
                                            ),
                                            value=["Select All"],
                                            multi=True,
                                            style=dropdown_style,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                # Date Range
                                html.Div(
                                    [
                                        html.Label(
                                            "Date Range:",
                                            style={
                                                "fontWeight": "bold",
                                                "marginBottom": "0.5rem",
                                                "color": "#495057",
                                            },
                                        ),
                                        dcc.DatePickerRange(
                                            id="date-picker",
                                            start_date=self.activities["date"].min(),
                                            end_date=self.activities["date"].max(),
                                            display_format="YYYY-MM-DD",
                                            style=date_picker_style,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                # Longest Activity Filter
                                html.Div(
                                    [
                                        html.Label(
                                            "Filters:",
                                            style={
                                                "fontWeight": "bold",
                                                "marginBottom": "0.5rem",
                                                "color": "#495057",
                                            },
                                        ),
                                        dcc.Checklist(
                                            id="checkbox-longest-activity",
                                            options=[
                                                {
                                                    "label": "Show Only Longest Distance Activities",
                                                    "value": "LONGEST",
                                                }
                                            ],
                                            value=[],
                                            inline=True,
                                            style=checkbox_style,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    style=card_style,
                ),
                # Map Card
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    "🗺️ Activity Map",
                                    style={"margin": "0", "color": "#495057"},
                                )
                            ],
                            style={
                                "backgroundColor": "#e9ecef",
                                "borderRadius": "8px 8px 0 0",
                            },
                        ),
                        dbc.CardBody(
                            [
                                dcc.Graph(
                                    id="graph-content",
                                    config={"scrollZoom": True},
                                    style=graph_style,
                                )
                            ]
                        ),
                    ],
                    style=card_style,
                ),
            ],
            fluid=True,
            style=container_style,
            className="px-0",
        )

        @callback(
            Output("graph-content", "figure"),
            Input("dropdown-multi-selection", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("checkbox-longest-activity", "value"),
        )
        def update_graph(activity, start_date, end_date, longest_filter):
            filter_start_date = self.activities["date"].astype(str) >= start_date
            filter_end_date = self.activities["date"].astype(str) <= end_date
            filter_activities = (
                self.activities["activity_name_and_date"].isin(activity)
            ) | ("Select All" in activity)
            filter_longest_activity = (self.activities["longest_activity"]) | (
                "LONGEST" not in longest_filter
            )

            df = self.activities[
                filter_start_date
                & filter_end_date
                & filter_activities
                & filter_longest_activity
            ].copy()

            fig = px.scatter_mapbox(
                df,
                lat="lat",
                lon="long",
                hover_data=["activity_name", "date", "distance"],
                zoom=8,
                color="activity_type",
                center={"lat": -33.55, "lon": -70.60},
                width=None,
                height=600,
                color_discrete_map={
                    "Run": "#ff6b6b",
                    "Ride": "#4ecdc4",
                    "Walk": "#45b7d1",
                    "Hike": "#96ceb4",
                    "Swim": "#feca57",
                },
            )
            fig.update_layout(
                mapbox_style="open-street-map",
                legend_title="Activity Type",
                legend=dict(
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1,
                    font=dict(size=12),
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                autosize=True,
                height=600,
            )

            # Enhanced hover template
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>"
                + "Date: %{customdata[1]}<br>"
                + "Distance: %{customdata[2]}<br>"
                + "<extra></extra>",
                marker=dict(size=8, opacity=0.7),
            )

            return fig

    def _open_browser(self):
        if not self.debug:
            webbrowser.open_new(f"http://127.0.0.1:{self.port}/")

    def run_app(self):
        Timer(1, self._open_browser).start()
        self.app.run(debug=self.debug, port=self.port)
