# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

The project has three independent entry points: fetch data, run the dashboard, send Telegram alerts. Each runs on its own — the dashboard does not auto-fetch.

```bash
# Install dependencies
poetry install

# 1. Fetch new Strava data (GPS streams + training log). --days controls the training-log window.
poetry run python fetch.py --days 7
poetry run python fetch.py --skip-gps --days 14   # only refresh training log
poetry run python fetch.py --skip-log             # only refresh GPS streams

# 2. Run the dashboard (reads cached CSVs only — no Strava auth)
poetry run python app.py

# 3. 48h-no-training Telegram alert (cron target)
poetry run python alert.py

# Lint and format (runs automatically via pre-commit)
poetry run ruff --fix .
poetry run ruff format .

# Install pre-commit hooks
pre-commit install

# GoPro video overlay
poetry run gopro-dashboard.py ~/Downloads/test.mp4 ~/Downloads/test_dashboard.mp4 --font '/Users/bmoreno/Library/Fonts/Roboto[wdth,wght].ttf' --units-speed kph
```

**Requirements**: A `.env` file with:
- `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` — needed by `fetch.py` to talk to Strava
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — needed by `alert.py` to send messages

## Architecture

This is a **Plotly Dash** web application (Python) that fetches GPS activity data from the Strava API and displays it on an interactive map. A second Training Log tab tracks daily training sessions and a standalone alert script sends a Telegram message after a 48h training gap.

### Data Flow

1. `fetch.py` — top-level Strava fetcher; auths once and runs both `download_strava_activities` (GPS streams) and `fetch_training_log` (training-log CSV)
2. `app.py` — slim dashboard launcher; loads `all_activities.csv` + `training_log.csv` and serves the Dash UI
3. `alert.py` — top-level cron entry; checks `training_log.csv` for the last activity, sends Telegram if the gap exceeds `TRAINING_LOG_GAP_HOURS` (48h)
4. `src/strava_connection.py` — handles Strava OAuth2 flow using `stravalib`
5. `src/strava_listing.py` — `list_activities(client, after, sport_types)` — shared helper used by both fetch flows
6. `src/download_strava_activities.py` — fetches GPS streams (latlng, altitude) for each activity and saves them as individual CSVs in `data/`. Skips WeightTraining, Workout, VirtualRide, and Treadmill (no-GPS types). Files are named `{activity_name}__{YYYYMMDD}.csv`.
7. `src/read_activities_data.py` — merges all CSVs into a consolidated `all_activities.csv` and marks the longest activity per type
8. `src/training_log/` — training-log subsystem:
   - `fetcher.py` — pulls metadata-only activities for the whitelisted types and writes `data/training_log.csv` with columns `activity_id, timestamp, activity_type, duration_seconds, metadata` (metadata is sparse JSON with calories / distance_km / pace as available)
   - `store.py` — load/upsert helpers with dedupe on `activity_id`
   - `alert_check.py` — gap detection + Telegram POST; keeps `.alert_state.json` to avoid duplicate alerts per gap
   - `layout.py` — Dash Training Log tab (summary cards, daily-minutes bar chart, calendar heatmap)
9. `src/dash_app.py` — builds and runs the Dash UI on port 8050; contains the `StravaActivitiesApp` class with the `dbc.Tabs` root layout
10. `src/create_manual_activity.py` — utility to generate circular GPS paths for manually created activities

### Key Design Points

- Three commands stay decoupled: dashboard launches without Strava auth; fetch and alert run independently (typically on cron).
- Training-log whitelist (Run, WeightTraining, Swim, Ride, Snowboard, Tennis) lives in `src/config.py` as `TRAINING_LOG_WHITELIST`. The legacy GPS-stream blacklist is unrelated and stays in `download_strava_activities.py`.
- All timestamps are UTC. The alert uses `datetime.now(timezone.utc)` and `pd.to_datetime(..., utc=True)` to avoid local-tz drift.
- The map is centered on Santiago, Chile (-33.55, -70.60) using Plotly scatter mapbox
- Activity type colors are in `src/config.py:ACTIVITY_COLOR_MAP` (Run, Ride, Walk, Hike, Swim, WeightTraining, Snowboard, Tennis)
- UI uses Dash Bootstrap Components with the COSMO theme
- Linting/formatting is enforced via Ruff (pre-commit hooks)
