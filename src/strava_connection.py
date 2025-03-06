from stravalib import Client
import os 
from dotenv import load_dotenv

load_dotenv() 

def get_strava_authorization_code():

    client = Client()
    url = client.authorization_url(
        client_id=os.environ["CLIENT_ID"] ,
        redirect_uri="http://127.0.0.1:5000/authorization",
    ) 
    print("Enter to the link below and copy the strava code \n")
    print(url)
    print("\n")

def get_strava_token(code):

    client = Client()
    token_response = client.exchange_code_for_token(
        client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"], code=code
    )

    return token_response

def strava_login(token_response):

    client = Client(
        access_token=token_response["access_token"],
    )

    athlete = client.get_athlete()
    print(f"Hi, {athlete.firstname} Welcome to stravalib!")

    return client 

def strava_connection(): 

    get_strava_authorization_code()
    code = input("Insert Autorization Code: ")
    token_response = get_strava_token(code)
    client = strava_login(token_response)

    return client


