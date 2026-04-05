import webbrowser
import pycountry
import plotly.express as px
import dash_bootstrap_components as dbc
from threading import Timer
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dcc, callback, Output, Input

from src import config
from src.styles import (
    CARD_STYLE,
    CHECKBOX_STYLE,
    CONTAINER_STYLE,
    DATE_PICKER_STYLE,
    DROPDOWN_STYLE,
    GRAPH_STYLE,
    HEADER_STYLE,
)


def _country_flag(cc: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in cc.upper())


def _country_name(cc: str) -> str:
    country = pycountry.countries.get(alpha_2=cc)
    return country.name if country else cc


class StravaActivitiesApp:
    def __init__(self, activities, favicon, debug, port="8050"):
        self.activities = activities
        self.app = Dash(external_stylesheets=[dbc.themes.COSMO])
        self.app.title = "Strava Activities"
        self.app._favicon = favicon
        self.port = port
        self.debug = debug
        load_figure_template("COSMO")

    def _apply_filters(self, df, activity, start_date, end_date, longest_filter):
        filter_start_date = df["date"].astype(str) >= start_date
        filter_end_date = df["date"].astype(str) <= end_date
        filter_activities = (df["activity_name_and_date"].isin(activity)) | (
            "Select All" in activity
        )
        filter_longest_activity = (df["longest_activity"]) | (
            "LONGEST" not in longest_filter
        )
        return df[
            filter_start_date
            & filter_end_date
            & filter_activities
            & filter_longest_activity
        ].copy()

    def _build_layout(self):
        return dbc.Container(
            [
                # Header
                html.Div(
                    [
                        html.H1(
                            children="🏃‍♂️ Strava Activities Map", style=HEADER_STYLE
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
                                            style=DROPDOWN_STYLE,
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
                                            style=DATE_PICKER_STYLE,
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
                                            style=CHECKBOX_STYLE,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    style=CARD_STYLE,
                ),
                # Visited Countries Card
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H4(
                                "🌍 Visited Countries",
                                style={"margin": "0", "color": "#495057"},
                            ),
                            style={
                                "backgroundColor": "#e9ecef",
                                "borderRadius": "8px 8px 0 0",
                            },
                        ),
                        dbc.CardBody(
                            [
                                html.Div(
                                    id="countries-summary",
                                    style={
                                        "fontWeight": "bold",
                                        "marginBottom": "0.5rem",
                                        "color": "#495057",
                                    },
                                ),
                                html.Div(id="countries-list"),
                            ]
                        ),
                    ],
                    style=CARD_STYLE,
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
                                    style=GRAPH_STYLE,
                                )
                            ]
                        ),
                    ],
                    style=CARD_STYLE,
                ),
            ],
            fluid=True,
            style=CONTAINER_STYLE,
            className="px-0",
        )

    def _register_callbacks(self):
        @callback(
            Output("graph-content", "figure"),
            Input("dropdown-multi-selection", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("checkbox-longest-activity", "value"),
        )
        def update_graph(activity, start_date, end_date, longest_filter):
            df = self._apply_filters(
                self.activities, activity, start_date, end_date, longest_filter
            )

            fig = px.scatter_mapbox(
                df,
                lat="lat",
                lon="lon",
                hover_data=["activity_name", "date", "distance"],
                zoom=8,
                color="activity_type",
                center=config.MAP_CENTER,
                width=None,
                height=600,
                color_discrete_map=config.ACTIVITY_COLOR_MAP,
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
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>"
                + "Date: %{customdata[1]}<br>"
                + "Distance: %{customdata[2]}<br>"
                + "<extra></extra>",
                marker=dict(size=8, opacity=0.7),
            )

            return fig

        @callback(
            Output("countries-summary", "children"),
            Output("countries-list", "children"),
            Input("dropdown-multi-selection", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("checkbox-longest-activity", "value"),
        )
        def update_countries(activity, start_date, end_date, longest_filter):
            df = self._apply_filters(
                self.activities, activity, start_date, end_date, longest_filter
            )
            unique_countries = sorted(df["country"].dropna().unique())
            count = len(unique_countries)
            summary = f"{count} {'country' if count == 1 else 'countries'} visited"
            badges = [
                dbc.Badge(
                    f"{_country_flag(cc)} {_country_name(cc)}",
                    color="light",
                    text_color="dark",
                    className="me-1 mb-1",
                    style={"fontSize": "0.85rem"},
                )
                for cc in unique_countries
            ]
            return summary, badges

    def create_app(self):
        self.app.layout = self._build_layout()
        self._register_callbacks()

    def _open_browser(self):
        if not self.debug:
            webbrowser.open_new(f"http://127.0.0.1:{self.port}/")

    def run_app(self):
        Timer(1, self._open_browser).start()
        self.app.run(debug=self.debug, port=self.port)
