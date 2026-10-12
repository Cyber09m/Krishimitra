import json
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db, limiter
from models import new_scan_doc, serialize_doc
from utils.vision_client import detect_disease, VisionError

disease_bp = Blueprint("disease", __name__)

with open(os.path.join(os.path.dirname(__file__), "..", "data", "treatments.json")) as f:
    TREATMENTS = json.load(f)


def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@disease_bp.post("/detect")
@jwt_required()
@limiter.limit("20 per minute")  # Gemini vision calls have quota/cost — protect against abuse
def detect():
    """
    Accepts a multipart/form-data upload under the field name 'image'.
    Flow: validate -> Gemini vision inference -> confidence threshold
    check -> treatment lookup -> persist scan -> respond.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided (expected field 'image')."}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"error": "Empty filename."}), 400
    if not _allowed_file(image.filename):
        return jsonify({
            "error": f"Unsupported file type. Allowed: {sorted(current_app.config['ALLOWED_IMAGE_EXTENSIONS'])}"
        }), 400

    image_bytes = image.read()
    max_bytes = current_app.config["MAX_IMAGE_SIZE_MB"] * 1024 * 1024
    if len(image_bytes) > max_bytes:
        return jsonify({"error": f"Image exceeds {current_app.config['MAX_IMAGE_SIZE_MB']}MB limit."}), 413

    try:
        result = detect_disease(image_bytes, image.filename)
    except VisionError as exc:
        return jsonify({"error": str(exc)}), 502

    predicted_class = result["class"]
    confidence = round(result["confidence"], 4)
    threshold = current_app.config["DISEASE_CONFIDENCE_THRESHOLD"]
    needs_review = confidence < threshold

    treatment_info = TREATMENTS.get(predicted_class, {
        "label": predicted_class,
        "severity": "unknown",
        "description": "This disease class isn't in our treatment library yet.",
        "treatment": "Please consult a local agricultural extension officer for guidance.",
    })

    user_id = get_jwt_identity()
    scan_doc = new_scan_doc(
        user_id=user_id,
        image_filename=image.filename,
        prediction=predicted_class,
        confidence=confidence,
        treatment=treatment_info,
        needs_review=needs_review,
    )
    inserted = db.scan_history.insert_one(scan_doc)

    return jsonify({
        "scan": serialize_doc({**scan_doc, "_id": inserted.inserted_id}),
        "needs_review": needs_review,
        "message": (
            "Confidence is below our review threshold — treat this as a "
            "preliminary result and consider a second photo or expert review."
            if needs_review else
            "Diagnosis complete."
        ),
    }), 200


@disease_bp.get("/history")
@jwt_required()
def history():
    from bson import ObjectId
    user_id = get_jwt_identity()
    scans = db.scan_history.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(50)
    return jsonify({"scans": [serialize_doc(s) for s in scans]}), 200
