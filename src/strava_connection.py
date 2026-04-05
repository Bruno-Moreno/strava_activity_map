import json
import os
import time
import webbrowser
from stravalib import Client

TOKEN_PATH = ".strava_token.json"


def _save_token(token_response):
    with open(TOKEN_PATH, "w") as f:
        json.dump(
            {
                "access_token": token_response["access_token"],
                "refresh_token": token_response["refresh_token"],
                "expires_at": token_response["expires_at"],
            },
            f,
        )


def _load_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH) as f:
        return json.load(f)


def _oauth_flow():
    client = Client()
    url = client.authorization_url(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        redirect_uri="http://127.0.0.1:5000/authorization",
    )
    print(
        "Open the link below, authorize, then paste the code from the redirect URL:\n"
    )
    print(f"{url}\n")
    webbrowser.open(url)
    code = input("Insert Authorization Code: ")
    token_response = client.exchange_code_for_token(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        code=code,
    )
    _save_token(token_response)
    return token_response


def strava_connection():
    token = _load_token()

    if token is None:
        print("No saved token found — starting OAuth flow.")
        token = _oauth_flow()
    elif token["expires_at"] < time.time():
        print("Token expired — refreshing automatically.")
        client = Client()
        token = client.refresh_access_token(
            client_id=os.environ["STRAVA_CLIENT_ID"],
            client_secret=os.environ["STRAVA_CLIENT_SECRET"],
            refresh_token=token["refresh_token"],
        )
        _save_token(token)

    client = Client(
        access_token=token["access_token"],
        refresh_token=token["refresh_token"],
        token_expires=token["expires_at"],
    )
    athlete = client.get_athlete()
    print(f"Hi, {athlete.firstname}! Connected to Strava.")

    return client
