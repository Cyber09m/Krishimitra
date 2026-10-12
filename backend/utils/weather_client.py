"""
Weather + rule-based farming advisory, backed by Open-Meteo (free, no API
key, no rate-limit wall at this scale of usage).

Design note on "real-time": the underlying forecast models themselves only
update hourly at the source, so refetching every second would just replay
the same numbers while burning requests. We cache each location's forecast
for WEATHER_CACHE_SECONDS and let the *frontend* provide the live, ticking
feel (see Weather.jsx) — this is the same pattern real weather apps use.
"""
import time
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CACHE_SECONDS = 60
_geocode_cache = {}
_forecast_cache = {}

WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"), 3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"), 48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Moderate drizzle", "🌦️"), 55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"), 73: ("Moderate snow", "🌨️"), 75: ("Heavy snow", "❄️"),
    80: ("Slight rain showers", "🌦️"), 81: ("Moderate rain showers", "🌧️"), 82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm with hail", "⛈️"), 99: ("Severe thunderstorm with hail", "⛈️"),
}


class WeatherError(Exception):
    pass


def _describe_code(code):
    return WMO_CODES.get(code, ("Unknown", "❓"))


def geocode(place_name: str):
    key = place_name.strip().lower()
    if key in _geocode_cache:
        return _geocode_cache[key]

    try:
        resp = requests.get(GEOCODE_URL, params={"name": place_name, "count": 1}, timeout=8)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherError(f"Location lookup failed: {exc}") from exc

    results = resp.json().get("results")
    if not results:
        raise WeatherError(f"Couldn't find a location matching '{place_name}'.")

    top = results[0]
    resolved = (top["latitude"], top["longitude"], f"{top['name']}, {top.get('admin1', top.get('country', ''))}")
    _geocode_cache[key] = resolved
    return resolved


def get_forecast(lat: float, lon: float):
    cache_key = (round(lat, 2), round(lon, 2))
    cached = _forecast_cache.get(cache_key)
    if cached and (time.time() - cached[0]) < WEATHER_CACHE_SECONDS:
        return cached[1]

    try:
        resp = requests.get(FORECAST_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "timezone": "auto",
            "forecast_days": 3,
        }, timeout=8)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherError(f"Weather fetch failed: {exc}") from exc

    data = resp.json()
    _forecast_cache[cache_key] = (time.time(), data)
    return data


def build_advisory(forecast: dict) -> list:
    """Deterministic rule-based farming advisory — no LLM, so it's
    auditable and never hallucinates a condition not present in the data."""
    advisories = []
    hourly = forecast.get("hourly", {})
    daily = forecast.get("daily", {})

    max_rain_prob = max((hourly.get("precipitation_probability") or [0])[:24] or [0])
    current = forecast.get("current", {})
    wind_speed = current.get("wind_speed_10m", 0)
    today_max_temp = (daily.get("temperature_2m_max") or [None])[0]
    today_min_temp = (daily.get("temperature_2m_min") or [None])[0]

    if max_rain_prob >= 60:
        advisories.append({
            "level": "warning",
            "message": f"Heavy rain likely in the next 24h ({max_rain_prob}% chance) — "
                       f"delay pesticide/fertilizer spraying and check field drainage.",
        })
    if wind_speed and wind_speed >= 30:
        advisories.append({
            "level": "warning",
            "message": f"High wind currently ({wind_speed} km/h) — avoid spraying (drift risk) "
                       f"and secure any nets or covers.",
        })
    if today_max_temp is not None and today_max_temp >= 38:
        advisories.append({
            "level": "caution",
            "message": f"Heatwave conditions expected ({today_max_temp}°C) — irrigate early "
                       f"morning or evening to reduce evaporation loss.",
        })
    if today_min_temp is not None and today_min_temp <= 5:
        advisories.append({
            "level": "caution",
            "message": f"Cold snap expected (low of {today_min_temp}°C) — consider frost "
                       f"protection for sensitive crops overnight.",
        })
    if not advisories:
        advisories.append({
            "level": "ok",
            "message": "Conditions look stable for the next 24h — normal farm operations advised.",
        })
    return advisories


def get_weather_report(location_name: str) -> dict:
    lat, lon, resolved_name = geocode(location_name)
    forecast = get_forecast(lat, lon)

    current = forecast.get("current", {})
    code_label, code_emoji = _describe_code(current.get("weather_code"))

    return {
        "location": resolved_name,
        "coordinates": {"lat": lat, "lon": lon},
        "current": {
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "precipitation_mm": current.get("precipitation"),
            "condition": code_label,
            "icon": code_emoji,
            "observed_at": current.get("time"),
        },
        "daily_forecast": [
            {
                "date": forecast["daily"]["time"][i],
                "max_temp_c": forecast["daily"]["temperature_2m_max"][i],
                "min_temp_c": forecast["daily"]["temperature_2m_min"][i],
                "rain_probability_pct": forecast["daily"]["precipitation_probability_max"][i],
                "condition": _describe_code(forecast["daily"]["weather_code"][i])[0],
                "icon": _describe_code(forecast["daily"]["weather_code"][i])[1],
            }
            for i in range(len(forecast["daily"]["time"]))
        ],
        "advisory": build_advisory(forecast),
        "cache_seconds": WEATHER_CACHE_SECONDS,
    }
