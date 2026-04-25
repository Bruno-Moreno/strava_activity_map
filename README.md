# Strava Activity Map

Plotly Dash web app that fetches GPS activity data from the Strava API and displays it on an interactive map.

![Strava Map](/img/strava_map.PNG)

## Features

- Interactive map of GPS activities (Run, Ride, Walk, Hike, Swim, Snowboard, and more)
- Filter by activity name, date range, or show only the longest distance per activity type
- Visited Countries panel with flag display
- GoPro video GPS overlay support via `gopro-overlay`

## Requirements

A `.env` file with `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` is required to download activities from Strava.

## Installation

```bash
# Python 3.11+ required
pyenv install 3.11
pyenv local 3.11

poetry install

# Optional: enable pre-commit hooks (ruff lint + format)
pre-commit install
```

## Running

```bash
poetry run python app.py
```

The app opens automatically on [http://localhost:8050](http://localhost:8050).

## Project Structure

```
app.py                          # Entry point: connect → download → load → launch
src/
  strava_connection.py          # Strava OAuth2 flow
  download_strava_activities.py # Fetch GPS streams and save to data/ as CSVs
  read_activities_data.py       # Merge CSVs into all_activities.csv
  dash_app.py                   # Dash UI, layout, and callbacks
  create_manual_activity.py     # Generate circular GPS paths for manual activities
  config.py                     # Map center, activity colors, type blacklist
data/                           # Per-activity CSV files ({name}__{YYYYMMDD}.csv)
```

Filtered activity types (not downloaded): `WeightTraining`, `Workout`, `VirtualRide`, `Treadmill`.

## GoPro Video Overlay

```bash
poetry run gopro-dashboard.py ~/Downloads/test.mp4 ~/Downloads/test_dashboard.mp4 \
  --font '/Users/bmoreno/Library/Fonts/Roboto[wdth,wght].ttf' \
  --units-speed kph
```

Requires `ffmpeg` installed on the system.

## Dependencies

| Package | Version |
|---|---|
| Python | >=3.11 |
| dash | ^3.0 |
| plotly | ^6.0 |
| stravalib | ^2.2 |
| dash-bootstrap-components | ^1.7 |
| gopro-overlay | ^0.129 |
| reverse_geocoder | ^1.5 |
| pycountry | ^24.6 |
