"""
Main Flask application
Web app captures images, detects emotions, and recommends playlists that correlate to the emotion.
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_login import LoginManager, login_required, current_user
import certifi

# load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# flask-login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

from bson.objectid import ObjectId
from auth import auth_bp, User


# user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# register the auth blueprint
app.register_blueprint(auth_bp)

# db setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = mongo_client["emotion_playlist"]
emotion_db = db["emotions"]
playlist_db = db["playlists"]

DEFAULT_EMOTION_DATA = {
    "angry": "😡",
    "disgust": "🤢",
    "fear": "😖",
    "happy": "😂",
    "neutral": "😑",
    "sad": "🥲",
    "surprise": "😱",
}

playlistName = ""  # emotion is stored here to be used in spotify API


# sample home page
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html", user=current_user)


@app.route("/submit-video", methods=["POST"])
@login_required
def submit_video():
    """Handle image submission, analyze emotion, and return the result."""
    data = request.get_json()
    base64_img = data.get("image")

    if not base64_img:
        return jsonify({"error": "No image provided"}), 400

    # print("Received base64 image:", base64_img[:100])  #for debugging - print first 100 characters (don't log the entire string)

    try:
        # call the ML microservice
        resp = requests.post(
            "http://localhost:6001/detect", json={"image": base64_img}, timeout=10
        )
        resp.raise_for_status()
        emotion = resp.json().get("emotion")
        print("Detected emotion:", emotion)  # Debugging output

        if emotion:
            emotion_record = {
                "user_id": current_user.id,
                "emotion": emotion,
                "user_agent": request.headers.get("User-Agent"),
            }
            emotion_db.insert_one(emotion_record)

    except Exception as e:
        print(f"Error detecting emotion-SUBMIT: {e}")
        return jsonify({"emotion": "unknown", "emoji": "🤔"})

    DEFAULT_EMOTION_DATA = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "surprise": "😮",
        "neutral": "😐",
        "fear": "😨",
        "disgust": "🤢",
    }

    if emotion:
        emoji = DEFAULT_EMOTION_DATA.get(emotion, "🤔")
        playlistName = emotion
        return jsonify({"emotion": emotion, "emoji": emoji})

    return jsonify({"emotion": "unknown", "emoji": "🤔"})


@app.route("/detect", methods=["POST"])
def detect_emotion(base64_image):
    """Detect emotion by sending base64 image to the ML client."""
    try:
        response = requests.post(
            "http://localhost:6001/detect", json={"image": base64_image}, timeout=10
        )
        response.raise_for_status()
        playlistName = response.json().get("emotion")
        return response.json().get("emotion")
    except Exception as e:
        print(f"Error detecting emotion-DETECT: {e}")
        return None


@app.route("/my-songs")
@login_required
def my_songs():
    """Show playlists that were generated for a user"""

    users_emotions = list(emotion_db.find({"user_id": current_user.id}))
    songs = []

    for i in users_emotions:
        emotion = i.get("emotion")

        if emotion:

            collection_name = emotion.lower()
            if collection_name in db.list_collection_names():
                song = db[collection_name].find_one()
            else:
                song = None

            if song:
                if "_id" in song:
                    song["_id"] = str(song["_id"])

                songs.append(
                    {
                        "emotion": emotion,
                        "emoji": DEFAULT_EMOTION_DATA.get(emotion, "🤔"),
                        "song": song,
                    }
                )
            else:
                # add without song (remove this?)
                i.append(
                    {
                        "emotion": emotion,
                        "emoji": DEFAULT_EMOTION_DATA.get(emotion, "🤔"),
                        "song": None,
                    }
                )

    return render_template("my_songs.html", songs=songs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
