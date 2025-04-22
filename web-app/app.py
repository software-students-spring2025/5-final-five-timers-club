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

    try:
        emotion = detect_emotion(base64_img)
        print("Detected emotion:", emotion) #debugging
    except Exception as e:
        print(f"Error detecting emotion: {e}")
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
        return jsonify({"emotion": emotion, "emoji": emoji})
    
    return jsonify({"emotion": "unknown", "emoji": "🤔"})

@app.route("/detect", methods=["POST"])
def detect_emotion(base64_image):
    """Detect emotion by sending base64 image to the ML container."""
    try:
        response = requests.post(
            #'http://ml:6000/detect',
            json={'image': base64_image},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('emotion')
    except Exception as e:
        print(f"Error detecting emotion: {e}")
        return None