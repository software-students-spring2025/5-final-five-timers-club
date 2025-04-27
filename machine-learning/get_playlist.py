import os
import base64
from dotenv import load_dotenv
from requests import post, get
from pymongo import MongoClient

load_dotenv()

CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MONGO_URI     = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# setting up cache
mongo_client = MongoClient(MONGO_URI)
db           = mongo_client["emotion_playlist"]
spotify_db   = db["data"]


def get_token():
    """Fetch a fresh client-credentials token."""
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    resp = post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type":  "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_playlist_uri(token, emotion):
    """Search Spotify for up to 5 playlists matching `emotion`, skip any nulls, and return the first valid URI."""
    url     = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params  = {
        "q": emotion,
        "type": "playlist",
        "limit": 5
    }

    # let's fetch up to 5 results for now
    resp = get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json() or {}

    # pulling out the list, might contain nulls :(
    raw_items = data.get("playlists", {}).get("items", [])
    # attempt to filter out any null entries
    items = [pl for pl in raw_items if pl and pl.get("uri")]

    if not items:
        print(f"▶ No valid playlists found for emotion: {emotion}")
        return None

    # take the first good one (CHANGE FOR RANDOMIZATION OF THE PLAYLISTS LATER)
    first = items[0]
    uri   = first["uri"]

    # cache it
    spotify_db.update_one(
        {"type": "playlist", "emotion": emotion},
        {"$set": {
            "uri":         uri,
            "name":        first.get("name", ""),
            "description": first.get("description", "")
        }},
        upsert=True
    )

    return uri



