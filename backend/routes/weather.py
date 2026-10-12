from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from extensions import db
from utils.weather_client import get_weather_report, WeatherError

weather_bp = Blueprint("weather", __name__)


@weather_bp.get("/current")
@jwt_required()
def current():
    """
    GET /api/weather/current?location=Ayodhya
    If 'location' is omitted, falls back to the farmer's saved profile state.
    """
    location = request.args.get("location")

    if not location:
        user_id = get_jwt_identity()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        location = (user or {}).get("profile", {}).get("state")

    if not location:
        return jsonify({
            "error": "No location provided and no state saved in your profile. "
                     "Pass ?location=<city or state>, or update your profile."
        }), 400

    try:
        report = get_weather_report(location)
    except WeatherError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(report), 200
