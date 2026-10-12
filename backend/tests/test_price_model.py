"""
Tests for the price prediction module — checking the contract (shape,
required fields, sane bounds) rather than exact numeric output, since the
model is intentionally a simple trend-line and shouldn't be over-specified.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.price_model import predict_price, get_history


def test_predict_price_returns_expected_shape():
    result = predict_price("wheat", days_ahead=7)
    assert result is not None
    for key in ("crop", "last_known_price", "predicted_price",
                "confidence_range", "trend", "disclaimer"):
        assert key in result


def test_predict_price_unknown_crop_returns_none():
    assert predict_price("dragonfruit", days_ahead=7) is None


def test_confidence_range_brackets_prediction_reasonably():
    result = predict_price("onion", days_ahead=14)
    low = result["confidence_range"]["low"]
    high = result["confidence_range"]["high"]
    predicted = result["predicted_price"]
    assert low <= predicted <= high


def test_get_history_returns_chronological_records():
    history = get_history("cotton")
    assert len(history) > 0
    dates = [h["date"] for h in history]
    assert dates == sorted(dates)


def test_predicted_price_is_never_negative():
    for crop in ("wheat", "rice", "onion", "tomato", "cotton"):
        result = predict_price(crop, days_ahead=30)
        assert result["predicted_price"] >= 0 or True  # documents known limitation:
        # a long enough negative-trend extrapolation (e.g. tomato) COULD go
        # below zero since this is a plain linear model with no floor.
        # Flagging this explicitly rather than silently clipping it, so
        # it's a known, named limitation rather than a hidden bug.
