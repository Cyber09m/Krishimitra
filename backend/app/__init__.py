from flask import Flask
from flask_cors import CORS
from datetime import timedelta

from config import Config
from extensions import jwt, init_mongo, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=config_class.JWT_ACCESS_TOKEN_EXPIRES_MIN
    )

    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    jwt.init_app(app)
    limiter.init_app(app)
    init_mongo(app)

    # --- Blueprints ---
    from routes.auth import auth_bp
    from routes.disease import disease_bp
    from routes.chatbot import chatbot_bp
    from routes.price import price_bp
    from routes.schemes import schemes_bp
    from routes.weather import weather_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(disease_bp, url_prefix="/api/disease")
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")
    app.register_blueprint(price_bp, url_prefix="/api/price")
    app.register_blueprint(schemes_bp, url_prefix="/api/schemes")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "krishimitra-api"}

    return app
