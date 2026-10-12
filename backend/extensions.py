"""
Shared extension instances, created once here and initialized on the app
in app/__init__.py. Keeping them here (rather than instantiating inside
create_app) avoids circular imports between routes/*.py and the app factory.
"""
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt as bcrypt_lib

jwt = JWTManager()

# Rate limiting: in-memory storage is fine for a single-process dev/demo
# deployment. For multi-worker production, point storage_uri at Redis
# (e.g. "redis://localhost:6379") so all workers share the same counters.
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])

_mongo_client = None
db = None


def init_mongo(app):
    global _mongo_client, db
    _mongo_client = MongoClient(app.config["MONGO_URI"])
    db = _mongo_client[app.config["MONGO_DB_NAME"]]

    # Helpful indexes — created idempotently at startup.
    db.users.create_index("email", unique=True)
    db.scan_history.create_index("user_id")
    db.chat_logs.create_index("user_id")
    return db


def hash_password(plain_password: str) -> bytes:
    return bcrypt_lib.hashpw(plain_password.encode("utf-8"), bcrypt_lib.gensalt())


def check_password(plain_password: str, hashed: bytes) -> bool:
    try:
        return bcrypt_lib.checkpw(plain_password.encode("utf-8"), hashed)
    except (ValueError, TypeError):
        return False
