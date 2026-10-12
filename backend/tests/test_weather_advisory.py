"""
Tests for the rule-based farm advisory engine — built with synthetic
forecast payloads shaped like Open-Meteo's real response, so no network
call or API key is needed to run these.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.weather_client import build_advisory


def _fake_forecast(rain_probs=None, wind_speed=5, max_temp=28, min_temp=18):
    return {
        "current": {"wind_speed_10m": wind_speed},
        "hourly": {"precipitation_probability": rain_probs or [10] * 24},
        "daily": {
            "temperature_2m_max": [max_temp],
            "temperature_2m_min": [min_temp],
        },
    }


def test_heavy_rain_triggers_warning():
    forecast = _fake_forecast(rain_probs=[70] * 24)
    advisory = build_advisory(forecast)
    assert any(a["level"] == "warning" and "rain" in a["message"].lower() for a in advisory)


def test_high_wind_triggers_warning():
    forecast = _fake_forecast(wind_speed=35)
    advisory = build_advisory(forecast)
    assert any("wind" in a["message"].lower() for a in advisory)


def test_heatwave_triggers_caution():
    forecast = _fake_forecast(max_temp=41)
    advisory = build_advisory(forecast)
    assert any("heat" in a["message"].lower() for a in advisory)


def test_cold_snap_triggers_caution():
    forecast = _fake_forecast(min_temp=2)
    advisory = build_advisory(forecast)
    assert any("cold" in a["message"].lower() for a in advisory)


def test_calm_conditions_return_ok_status():
    forecast = _fake_forecast()
    advisory = build_advisory(forecast)
    assert len(advisory) == 1
    assert advisory[0]["level"] == "ok"
