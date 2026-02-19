# Strava Activity Map

Plotly Dash app with GPS Strava Activities. 

![Strava Map](/img/strava_map.PNG)

## How to Run

**Requirements**: To download the latest Strava activities from your account, it is mandatory to have a `.env` file with `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` variables declared. 

To execute the app `poetry run python app.py`

## Installation 

- Install pyenv python 3.10.X `pyenv install 3.10.4`
- Set the python version with `pyenv local 3.10.4` this creates the file `.python-version`
- `poetry env use 3.10.4`
- `poetry install`
- (optional) `pre-commit install`

## Others 

It is possible to get GPS data overlay on a video using `gopro-overlay` library and `ffmpeg`. Execute `poetry run gopro-dashboard.py ~/Downloads/test.mp4 ~/Downloads/test_dashboard.mp4 --font '/Users/bmoreno/Library/Fonts/Roboto[wdth,wght].ttf' --units-speed kph`