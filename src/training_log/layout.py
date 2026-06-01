from datetime import datetime, timedelta, timezone

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

from src.config import ACTIVITY_COLOR_MAP
from src.styles import CARD_STYLE


def _empty_state() -> html.Div:
    return html.Div(
        dbc.Alert(
            "No training logged yet — run `python fetch.py` first.",
            color="info",
        ),
        style=CARD_STYLE,
    )


def _summary_cards(df: pd.DataFrame) -> dbc.Row:
    ts = pd.to_datetime(df["timestamp"], utc=True)
    now = datetime.now(timezone.utc)
    last = ts.max().to_pydatetime()
    hours_since = (now - last).total_seconds() / 3600
    week_mask = ts >= (now - timedelta(days=7))
    sessions_week = int(week_mask.sum())
    minutes_week = int(df.loc[week_mask, "duration_seconds"].sum() / 60)

    def card(title: str, value: str) -> dbc.Col:
        return dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H6(title, style={"color": "#6c757d"}),
                        html.H3(value, style={"color": "#2c3e50", "margin": "0"}),
                    ]
                ),
                style=CARD_STYLE,
            )
        )

    return dbc.Row(
        [
            card("Hours since last training", f"{hours_since:.1f}"),
            card("Sessions this week", str(sessions_week)),
            card("Minutes this week", str(minutes_week)),
        ]
    )


def _daily_minutes_chart(df: pd.DataFrame) -> dcc.Graph:
    d = df.copy()
    d["date"] = pd.to_datetime(d["timestamp"], utc=True).dt.date
    d["minutes"] = d["duration_seconds"] / 60
    agg = d.groupby(["date", "activity_type"], as_index=False)["minutes"].sum().round(1)
    fig = px.bar(
        agg,
        x="date",
        y="minutes",
        color="activity_type",
        color_discrete_map=ACTIVITY_COLOR_MAP,
        title="Daily training minutes by type",
        labels={"minutes": "Minutes", "date": "Date", "activity_type": "Type"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return dcc.Graph(figure=fig)


def _calendar_heatmap(df: pd.DataFrame) -> dcc.Graph:
    d = df.copy()
    d["date"] = pd.to_datetime(d["timestamp"], utc=True).dt.date
    d["minutes"] = d["duration_seconds"] / 60
    daily = d.groupby("date", as_index=False)["minutes"].sum()
    daily["date"] = pd.to_datetime(daily["date"])

    start = daily["date"].min()
    end = daily["date"].max()
    full_range = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    daily = full_range.merge(daily, on="date", how="left").fillna({"minutes": 0})

    daily["weekday"] = daily["date"].dt.day_name()
    daily["week"] = daily["date"].dt.strftime("%Y-W%V")

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    pivot = daily.pivot_table(
        index="weekday",
        columns="week",
        values="minutes",
        aggfunc="sum",
        fill_value=0,
    ).reindex(weekday_order)

    fig = px.imshow(
        pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        color_continuous_scale="Greens",
        labels={"x": "Week", "y": "Day", "color": "Minutes"},
        aspect="auto",
        title="Training intensity (minutes per day)",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(side="bottom")
    return dcc.Graph(figure=fig)


def build_training_log_tab(df: pd.DataFrame) -> html.Div:
    if df is None or df.empty:
        return _empty_state()

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.H4(
                            "📊 Training Summary",
                            style={"margin": "0", "color": "#495057"},
                        ),
                        style={
                            "backgroundColor": "#e9ecef",
                            "borderRadius": "8px 8px 0 0",
                        },
                    ),
                    dbc.CardBody(_summary_cards(df)),
                ],
                style=CARD_STYLE,
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.H4(
                            "📈 Daily Minutes by Activity",
                            style={"margin": "0", "color": "#495057"},
                        ),
                        style={
                            "backgroundColor": "#e9ecef",
                            "borderRadius": "8px 8px 0 0",
                        },
                    ),
                    dbc.CardBody(_daily_minutes_chart(df)),
                ],
                style=CARD_STYLE,
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.H4(
                            "🗓️ Calendar Heatmap",
                            style={"margin": "0", "color": "#495057"},
                        ),
                        style={
                            "backgroundColor": "#e9ecef",
                            "borderRadius": "8px 8px 0 0",
                        },
                    ),
                    dbc.CardBody(_calendar_heatmap(df)),
                ],
                style=CARD_STYLE,
            ),
        ]
    )
