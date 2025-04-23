import base64
from flask import Flask, request, jsonify
from deepface import DeepFace
import cv2
import numpy as np
from get_playlist import get_playlist_uri, get_token

app = Flask(__name__)


# functions
def readb64(base64_string):
    """Decode base64 image to OpenCV format."""
    decoded_data = base64.b64decode(base64_string.split(",")[1])
    np_data = np.frombuffer(decoded_data, np.uint8)
    return cv2.imdecode(np_data, cv2.IMREAD_COLOR)


def detect_emotion(base64_image):
    try:
        img = readb64(base64_image)
        result = DeepFace.analyze(img, actions=["emotion"], enforce_detection=False)
        print("DeepFace result:", result)
        if not result or not isinstance(result, list):
            print("No face detected")
            return None

        return result[0]["dominant_emotion"]
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


@app.route("/playlist", methods=["POST"])
def get_playlist():
    """Detect emotion from image and return a Spotify playlist URI."""
    data = request.get_json()
    base64_image = data.get("image")

    if not base64_image:
        return jsonify({"error": "No image provided"}), 400

    emotion = detect_emotion(base64_image)

    if not emotion:
        return jsonify({"error": "Emotion detection failed"}), 400

    try:
        token = get_token()
        playlist_uri = get_playlist_uri(token, emotion)
    except Exception as e:
        print("Spotify error:", e)
        return jsonify({"emotion": emotion, "error": "Spotify request failed"}), 500

    if playlist_uri:
        return jsonify({"emotion": emotion, "playlist_uri": playlist_uri})
    else:
        return jsonify({"emotion": emotion, "error": "No playlist found"}), 404
