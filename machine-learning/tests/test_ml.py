import json
import base64
import sys
import os
from unittest.mock import patch, MagicMock
import pytest
import numpy as np
import cv2

"""Unit Testing for Machine Learning Client"""

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=import-error
# pylint: disable=wrong-import-position
from face_recog import app, readb64, detect_emotion
from get_playlist import get_token, get_song_by_emotion

# pylint: disable=redefined-outer-name


@pytest.fixture
def client():
    """Test for creating flask client"""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def test_b64():
    """Test for encoding to base64 string"""
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    # pylint: disable=no-member
    _, buffer = cv2.imencode(".jpg", image)
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"


def test_readb64(test_b64):
    """Test decoding base64 string"""
    output = readb64(test_b64)
    assert output is not None
    assert len(output) > 0
    assert output.shape == (10, 10, 3)


@patch("face_recog.DeepFace.analyze")
@patch("face_recog.model.insert_one")
def test_emotion_success(db, deepface, test_b64):
    """TEst detecting emotion"""
    deepface.return_value = [{"emotion": {"happy": 0.9}, "dominant_emotion": "happy"}]

    result = detect_emotion(test_b64)
    assert result == "happy"
    deepface.assert_called_once()
    db.assert_called_once()


@patch("face_recog.DeepFace.analyze")
def test_emotion_fail(deepface, test_b64):
    """Test error handling when detecting emotions"""
    deepface.side_effect = Exception("Test error")
    result = detect_emotion(test_b64)
    assert result is None


@patch("face_recog.detect_emotion")
def test_endpoints(detect, client, test_b64):
    """Test api endpoints"""
    detect.return_value = "happy"
    resp = client.post("/detect", json={"image": test_b64})

    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "emotion" in data
    assert data["emotion"] == "happy"


def test_endpoint_fail(client):
    """Test detecting endpoint when there is no image"""
    resp = client.post("/detect", json={})

    assert resp.status_code == 400
    output = json.loads(resp.data)
    assert "error" in output


# need to mock get function
@patch("face_recog.get_token")
def test_token(token, client):
    """Tests endpoint that gives token"""
    token.return_value = "test-token"

    resp = client.get("/token")

    assert resp.status_code == 200
    output = json.loads(resp.data)
    assert output["token"] == "test-token"


@patch("get_playlist.post")
def test_get_token(mock_post):
    """Test requesting auth token"""
    response = MagicMock()
    response.json.return_value = {"access_token": "test-token"}
    response.raise_for_status = MagicMock()
    mock_post.return_value = response

    res = get_token()

    assert res == "test-token"


@patch("face_recog.detect_emotion")
@patch("face_recog.get_token")
@patch("face_recog.get_song_by_emotion")
def test_playlist(get_song, token, detect, client, test_b64):
    """Test endpoint for emotion detection and music rec"""
    detect.return_value = "happy"
    token.return_value = "test-token"
    get_song.return_value = {
        "name": "Happy",
        "artist": "Test Artist",
        "_id": "1",
    }

    response = client.post("/playlist", json={"image": test_b64})

    output = json.loads(response.data)
    assert response.status_code == 200
    assert output["emotion"] == "happy"
    assert output["song"]["name"] == "Happy"


@patch("get_playlist.get")
@patch("get_playlist.db")
def test_get_song_success(db, mock_get):
    """Test searching spotify for song"""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Happy",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"name": "Test Album"},
                    "uri": "spotify:1",
                    "preview_url": "url",
                    "external_urls": {"spotify": "url"},
                }
            ]
        }
    }
    mock_get.return_value = resp

    db.__getitem__.return_value.insert_one.return_value = MagicMock(inserted_id="1")

    result = get_song_by_emotion("test-token", "happy")

    assert result is not None
    assert result["name"] == "Happy"
    assert "artist" in result
    assert result["artist"] == "Test Artist"


@patch("get_playlist.get")
def test_get_song_fail(get):
    """Test finding no songs for an emotion"""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"tracks": {"items": []}}
    get.return_value = response

    result = get_song_by_emotion("test-token", "happy")
    assert result is None
