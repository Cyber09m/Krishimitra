from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from extensions import db, limiter
from models import new_chat_log_doc, serialize_doc
from utils.scheme_matcher import match_schemes
from utils.gemini_client import ask_chatbot, GeminiError

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.post("/ask")
@jwt_required()
@limiter.limit("15 per minute")  # Gemini calls have quota limits — protect against abuse/runaway loops
def ask():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required."}), 400

    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found."}), 404

    profile = user.get("profile", {})
    # Deterministic eligibility first — the LLM never decides this.
    eligible_schemes = match_schemes(profile)

    try:
        reply = ask_chatbot(message, profile, eligible_schemes)
    except GeminiError as exc:
        current_app.logger.exception("Gemini call failed")
        return jsonify({"error": str(exc)}), 502

    matched_ids = [s["id"] for s in eligible_schemes]
    log_doc = new_chat_log_doc(user_id, message, reply, matched_ids)
    db.chat_logs.insert_one(log_doc)

    return jsonify({
        "response": reply,
        "matched_schemes": eligible_schemes,
    }), 200


@chatbot_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    logs = db.chat_logs.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(50)
    return jsonify({"logs": [serialize_doc(l) for l in logs]}), 200
