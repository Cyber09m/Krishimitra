from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from pymongo.errors import DuplicateKeyError

from extensions import db, hash_password, check_password, limiter
from models import new_user_doc, serialize_doc

auth_bp = Blueprint("auth", __name__)

VALID_ROLES = {"farmer", "admin"}


@auth_bp.post("/register")
@limiter.limit("5 per hour")  # slow down mass fake-account creation
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    profile = data.get("profile") or {}

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    # Role is intentionally NOT taken from the client for security — every
    # public signup becomes a "farmer"; admin accounts are provisioned
    # separately (see README: seeding an admin user).
    doc = new_user_doc(name, email, hash_password(password), role="farmer", profile={
        "state": profile.get("state"),
        "primary_crop": profile.get("primary_crop"),
        "land_size_acres": profile.get("land_size_acres"),
        "category": profile.get("category"),
    })

    try:
        result = db.users.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "An account with this email already exists."}), 409

    token = create_access_token(
        identity=str(result.inserted_id),
        additional_claims={"role": doc["role"], "name": doc["name"]},
    )
    return jsonify({
        "message": "Account created.",
        "access_token": token,
        "user": serialize_doc({**doc, "_id": result.inserted_id}),
    }), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")  # brute-force protection
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.users.find_one({"email": email})
    if not user or not check_password(password, user["password"]):
        # Same message for "no such user" and "wrong password" — never reveal
        # which one failed, that's a user-enumeration leak.
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": user["role"], "name": user["name"]},
    )
    return jsonify({
        "message": "Logged in.",
        "access_token": token,
        "user": serialize_doc(user),
    }), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    from bson import ObjectId
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": serialize_doc(user)}), 200


@auth_bp.put("/me/profile")
@jwt_required()
def update_profile():
    """Farmers update state/crop/land-size here — this profile is exactly
    what the scheme matcher and chatbot use for eligibility filtering."""
    from bson import ObjectId
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    profile_fields = {}
    for key in ("state", "primary_crop", "land_size_acres", "category"):
        if key in data:
            profile_fields[f"profile.{key}"] = data[key]

    if not profile_fields:
        return jsonify({"error": "No valid profile fields provided."}), 400

    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": profile_fields})
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "Profile updated.", "user": serialize_doc(user)}), 200
