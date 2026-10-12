from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from utils.price_model import predict_price, get_history

price_bp = Blueprint("price", __name__)


@price_bp.get("/history")
@jwt_required()
def history():
    crop = request.args.get("crop")
    market = request.args.get("market")
    if not crop:
        return jsonify({"error": "crop query param is required."}), 400

    data = get_history(crop, market)
    if not data:
        return jsonify({"error": f"No historical data found for crop '{crop}'."}), 404
    return jsonify({"crop": crop, "history": data}), 200


@price_bp.get("/predict")
@jwt_required()
def predict():
    crop = request.args.get("crop")
    market = request.args.get("market")
    days_ahead = request.args.get("days_ahead", default=7, type=int)

    if not crop:
        return jsonify({"error": "crop query param is required."}), 400
    if days_ahead <= 0 or days_ahead > 90:
        return jsonify({"error": "days_ahead must be between 1 and 90."}), 400

    result = predict_price(crop, days_ahead=days_ahead, market=market)
    if result is None:
        return jsonify({"error": f"No historical data found for crop '{crop}'."}), 404

    return jsonify(result), 200
