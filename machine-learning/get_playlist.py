import json
import base64
import os
from dotenv import load_dotenv
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
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
    token = result.json()["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def get_playlist_uri(token, emotion):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={emotion}&type=playlist&limit=1"

    result = get(url + query, headers=headers)
    result.raise_for_status()
    playlists = result.json()["playlists"]["items"]

    if playlists:
        return playlists[0]["uri"]
    else:
        return None
