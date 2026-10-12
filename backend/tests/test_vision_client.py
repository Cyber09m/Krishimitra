"""
Tests for the Gemini vision client's response handling — mocked at the
HTTP layer so these run offline with no real API key or network call,
same philosophy as the other rule-based module tests.
"""
import sys
import os
import json
from unittest.mock import patch, MagicMock
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_app():
    """
    A bare Flask app with just the config keys vision_client.py reads —
    not the full create_app() factory, which eagerly connects to Mongo at
    startup (see extensions.init_mongo) and would make these tests need a
    live database for no reason relevant to what they're checking.
    """
    app = Flask(__name__)
    app.config.update(GEMINI_API_KEY="fake-key-for-tests", GEMINI_MODEL="gemini-flash-latest")
    return app


def _fake_gemini_response(class_name="Healthy", confidence=0.92):
    body = {
        "candidates": [{
            "content": {
                "parts": [{"text": json.dumps({"class": class_name, "confidence": confidence})}]
            }
        }]
    }
    mock_resp = MagicMock()
    mock_resp.json.return_value = body
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_known_class_and_confidence_are_parsed():
    from utils.vision_client import detect_disease
    app = _make_app()
    with app.app_context():
        with patch("utils.vision_client.requests.post", return_value=_fake_gemini_response("Tomato___Late_blight", 0.81)):
            result = detect_disease(b"fake-image-bytes", "leaf.jpg")
    assert result["class"] == "Tomato___Late_blight"
    assert result["confidence"] == 0.81


def test_missing_api_key_raises_vision_error():
    from utils.vision_client import detect_disease, VisionError
    app = Flask(__name__)
    app.config.update(GEMINI_API_KEY="", GEMINI_MODEL="gemini-flash-latest")
    with app.app_context():
        try:
            detect_disease(b"fake-image-bytes", "leaf.jpg")
            assert False, "expected VisionError"
        except VisionError as exc:
            assert "GEMINI_API_KEY" in str(exc)


def test_malformed_response_raises_vision_error():
    from utils.vision_client import detect_disease, VisionError
    app = _make_app()
    bad_response = MagicMock()
    bad_response.json.return_value = {"candidates": []}
    bad_response.raise_for_status.return_value = None
    with app.app_context():
        with patch("utils.vision_client.requests.post", return_value=bad_response):
            try:
                detect_disease(b"fake-image-bytes", "leaf.jpg")
                assert False, "expected VisionError"
            except VisionError:
                pass


def test_mime_type_detection():
    from utils.vision_client import _mime_type_for
    assert _mime_type_for("leaf.png") == "image/png"
    assert _mime_type_for("leaf.jpg") == "image/jpeg"
    assert _mime_type_for("leaf.jpeg") == "image/jpeg"
    assert _mime_type_for("leaf.webp") == "image/webp"
    assert _mime_type_for("leaf.unknownext") == "image/jpeg"  # sane fallback
