from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from extensions import db
from utils.scheme_matcher import match_schemes, get_all_schemes

schemes_bp = Blueprint("schemes", __name__)


@schemes_bp.get("/")
def list_all():
    return jsonify({"schemes": get_all_schemes()}), 200


@schemes_bp.get("/match")
@jwt_required()
def match_for_current_user():
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found."}), 404

    profile = user.get("profile", {})
    matches = match_schemes(profile)
    return jsonify({
        "profile_used": profile,
        "matched_count": len(matches),
        "schemes": matches,
    }), 200
