import json
import base64
import os
from dotenv import load_dotenv
from requests import post, get
from pymongo import MongoClient

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["emotion_playlist"]
spotify_db = db["data"]


def get_token():

    token = spotify_db.find_one({"type": "token"})

    if token and "access_token" in token:
        return token["access_token"]

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    result.raise_for_status()
    token_data = result.json()
    token = token_data["access_token"]

    spotify_db.update_one(
        {"type": "token"},
        {
            "$set": {
                "access_token": token,
                "expires_in": token_data["expires_in"],
            }
        },
        upsert=True,
    )

    return token


def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def get_playlist_uri(token, emotion):

    playlist = spotify_db.find_one({"type": "playlist", "emotion": emotion})

    if playlist and "uri" in playlist:
        return playlist["uri"]

    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={emotion}&type=playlist&limit=1"

    result = get(url + query, headers=headers)
    result.raise_for_status()
    playlists = result.json()["playlists"]["items"]

    if playlists:

        uri = playlists[0]["uri"]
        spotify_db.update_one(
            {"type": "playlist", "emotion": emotion},
            {
                "$set": {
                    "uri": uri,
                    "name": playlists[0]["name"],
                    "description": playlists[0]["description"],
                }
            },
            upsert=True,
        )

        return uri
    else:
        return None
