"""
Main Flask application
Web app captures images, detects emotions, and recommends playlists that correlate to the emotion.
"""

import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
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
    return render_template("index.html")


@app.route("/submit-video", methods=["POST"])
def submit_video():
    """Handle image submission, analyze emotion, and return the result."""
    data = request.get_json()
    base64_img = data.get("image")

    if not base64_img:
        return jsonify({"error": "No image provided"}), 400

    # print("Received base64 image:", base64_img[:100])  #for debugging - print first 100 characters (don't log the entire string)

    try:
        resp = requests.post(
            "http://localhost:6001/detect",
            json={"image": base64_img},
            timeout=10
        )
        resp.raise_for_status()
        emotion = resp.json().get("emotion")
        print("Detected emotion:", emotion)  # Debugging output

        if emotion:
            emotion_record = {
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
