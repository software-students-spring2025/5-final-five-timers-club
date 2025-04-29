import os
import base64
from dotenv import load_dotenv
from requests import post, get
from pymongo import MongoClient
import random

# load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["emotion_playlist"]


def get_token():
    """Fetch a fresh client-credentials token."""
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    resp = post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_song_by_emotion(token, emotion):
    """Search Spotify for a song matching the given emotion, return its data, and store it in the database."""
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": emotion, "type": "track", "limit": 5}

    resp = get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json() or {}

    raw_items = data.get("tracks", {}).get("items", [])
    items = [track for track in raw_items if track and track.get("uri")]

    if not items:
        print(f"▶ No valid songs found for emotion: {emotion}")
        return None

    first = random.choice(items)

    song_data = {
        "name": first.get("name", ""),
        "artist": first.get("artists", [{}])[0].get("name", ""),
        "album": first.get("album", {}).get("name", ""),
        "uri": first.get("uri", ""),
        "preview_url": first.get("preview_url", ""),
        "external_url": first.get("external_urls", {}).get("spotify", ""),
    }

    collection = db[emotion.lower()]
    result = collection.insert_one(song_data)

    song_copy = song_data.copy()
    song_copy["_id"] = str(result.inserted_id)

    return song_copy
