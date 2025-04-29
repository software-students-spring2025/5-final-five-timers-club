import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import os
import numpy as np
from get_playlist import get_song_by_emotion, get_token
from pymongo import MongoClient
from dotenv import load_dotenv

#load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["emotion_playlist"]
emotion_db = db["emotions"]
model = db["results"]


# functions
def readb64(base64_string):
    """Decode base64 image to OpenCV format."""
    decoded_data = base64.b64decode(base64_string.split(",")[1])
    np_data = np.frombuffer(decoded_data, np.uint8)
    # pylint: disable=no-member
    return cv2.imdecode(np_data, cv2.IMREAD_COLOR)


def detect_emotion(base64_image):
    try:
        img = readb64(base64_image)
        result = DeepFace.analyze(img, actions=["emotion"], enforce_detection=False)
        scores = result[0]["emotion"]
        dominant = result[0]["dominant_emotion"]
        to_store = {
            "main_emotion": dominant,
            "all_emotions": scores,
        }
        model.insert_one(to_store)
        return dominant
    except Exception as e:
        print("Emotion detection error:", e)
        return None


# endpoints
@app.route("/detect", methods=["POST"])
def detect():
    """Handle base64 image input and return detected emotion."""
    data = request.get_json()
    base64_image = data.get("image")

    if not base64_image:
        print("No image in request")
        return jsonify({"error": "No image provided"}), 400

    emotion = detect_emotion(base64_image)
    print("Detected emotion:", emotion)

    if emotion:
        return jsonify({"emotion": emotion})
    return jsonify({"error": "Could not detect emotion"}), 400


@app.route("/token", methods=["GET"])
def token():
    """Return a Spotify API token for Web Playback SDK"""
    try:
        t = get_token()
        return jsonify({"token": t})
    except Exception as e:
        print("Token error:", e)
        return jsonify({"error": "Could not fetch token"}), 500


@app.route("/playlist", methods=["POST"])
def playlist():
    img_b64 = request.json.get("image")
    if not img_b64:
        return jsonify(error="No image"), 400

    emotion = detect_emotion(img_b64)
    if not emotion:
        return jsonify(error="Detection failed"), 400

    try:
        token = get_token()
        song = get_song_by_emotion(token, emotion)
    except Exception as e:
        print("Spotify error:", e)
        return jsonify(error="Spotify request failed"), 500

    if not song:
        return jsonify(error="No song found"), 404

    return jsonify(emotion=emotion, song=song)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6001, debug=True)
