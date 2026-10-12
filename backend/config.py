import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central app configuration, pulled from environment variables.

    Nothing here is hard-coded on purpose: this same codebase should run
    unchanged across local dev, staging, and production simply by swapping
    the .env file / environment variables.
    """

    # --- Mongo ---
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "krishimitra")

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES_MIN = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MIN", 60))

    # --- Gemini (Google AI Studio) ---
    # Powers both the chatbot (utils/gemini_client.py) and disease detection
    # via image understanding (utils/vision_client.py) — one key, one
    # provider, no separate computer-vision account or training needed.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

    # --- CORS ---
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # --- Misc ---
    MAX_IMAGE_SIZE_MB = 8
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    DISEASE_CONFIDENCE_THRESHOLD = 0.70  # below this -> flag "needs_review"
