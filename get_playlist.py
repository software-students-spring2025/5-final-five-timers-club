import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_base64), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

token = get_token()

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

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

