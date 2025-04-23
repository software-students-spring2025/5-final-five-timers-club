from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEFAULT_EMOTION_DATA = {
    "angry": "😡",
    "disgust": "🤢",
    "fear": "😖",
    "happy": "😂",
    "neutral": "😑",
    "sad": "🥲",
    "surprise": "😱",
}

playlistName = "" #emotion is stored here to be used in spotify API

#sample home page
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

    #print("Received base64 image:", base64_img[:100])  #for debugging - print first 100 characters (don't log the entire string)

    try:
        emotion = detect_emotion(base64_img)
        print("Detected emotion:", emotion)  # Debugging output
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
        "disgust": "🤢"
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
            'http://localhost:6000/detect',
            json={'image': base64_image},
            timeout=10
        )
        response.raise_for_status()
        playlistName = response.json().get('emotion')
        return response.json().get('emotion')
    except Exception as e:
        print(f"Error detecting emotion-DETECT: {e}")
        return None