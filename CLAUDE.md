# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run the app
poetry run python app.py

# Lint and format (runs automatically via pre-commit)
poetry run ruff --fix .
poetry run ruff format .

# Install pre-commit hooks
pre-commit install

# GoPro video overlay
poetry run gopro-dashboard.py ~/Downloads/test.mp4 ~/Downloads/test_dashboard.mp4 --font '/Users/bmoreno/Library/Fonts/Roboto[wdth,wght].ttf' --units-speed kph
```

**Requirements**: A `.env` file with `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` is needed to download activities from Strava.

## Architecture

This is a **Plotly Dash** web application (Python) that fetches GPS activity data from the Strava API and displays it on an interactive map.

### Data Flow

1. `app.py` — entry point; orchestrates the full pipeline: connect → download → load → launch
2. `src/strava_connection.py` — handles Strava OAuth2 flow using `stravalib`
3. `src/download_strava_activities.py` — fetches GPS streams (latlng, altitude) for each activity and saves them as individual CSVs in `data/`. Skips WeightTraining, Workout, VirtualRide, and Treadmill activity types. Files are named `{activity_name}__{YYYYMMDD}.csv`.
4. `src/read_activities_data.py` — merges all CSVs into a consolidated `all_activities.csv` and marks the longest activity per type
5. `src/dash_app.py` — builds and runs the Dash UI on port 8050; contains the `StravaActivitiesApp` class with layout and callbacks
6. `src/create_manual_activity.py` — utility to generate circular GPS paths for manually created activities

### Key Design Points

- The map is centered on Santiago, Chile (-33.55, -70.60) using Plotly scatter mapbox
- Activity type colors: Run `#ff6b6b`, Ride `#4ecdc4`, Walk `#45b7d1`, Hike `#96ceb4`, Swim `#feca57`
- UI uses Dash Bootstrap Components with the COSMO theme
- Linting/formatting is enforced via Ruff (pre-commit hooks)
