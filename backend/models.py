"""
KrishiMitra doesn't use a heavyweight ODM — Mongo's documents map naturally
onto plain dicts, and Flask-PyMongo direct access keeps the data layer thin.
These helpers centralize the shape of each collection's documents so routes
don't repeat field names by hand.
"""
from datetime import datetime, timezone
from bson import ObjectId


def now():
    return datetime.now(timezone.utc)


def new_user_doc(name, email, hashed_password, role="farmer", profile=None):
    return {
        "name": name,
        "email": email.lower().strip(),
        "password": hashed_password,
        "role": role,  # "farmer" | "admin"
        "profile": profile or {
            "state": None,
            "primary_crop": None,
            "land_size_acres": None,
            "category": None,  # e.g. "small", "marginal", "large" — used by scheme matcher
        },
        "created_at": now(),
    }


def new_scan_doc(user_id, image_filename, prediction, confidence, treatment, needs_review):
    return {
        "user_id": ObjectId(user_id),
        "image_filename": image_filename,
        "prediction": prediction,
        "confidence": confidence,
        "treatment": treatment,
        "needs_review": needs_review,
        "created_at": now(),
    }


def new_chat_log_doc(user_id, message, response, matched_scheme_ids):
    return {
        "user_id": ObjectId(user_id),
        "message": message,
        "response": response,
        "matched_scheme_ids": matched_scheme_ids,
        "created_at": now(),
    }


def serialize_doc(doc):
    """Turn a Mongo document into JSON-safe output (ObjectId -> str, drop password)."""
    if doc is None:
        return None
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    if "user_id" in out and isinstance(out["user_id"], ObjectId):
        out["user_id"] = str(out["user_id"])
    out.pop("password", None)
    return out
