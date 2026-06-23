from datetime import timedelta
import logging
import os

from flask import Flask, request
from flask_cors import CORS


def create_app(initialize_callback):
    """Create and configure the Flask app."""
    app = Flask(__name__)

    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY env var is required")
    app.secret_key = secret
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

    is_production = os.getenv("FLASK_ENV") == "production"
    if is_production:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_DOMAIN"] = None
    else:
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_DOMAIN"] = None

    app.config["SESSION_COOKIE_HTTPONLY"] = True

    logging.debug("Using enhanced Flask sessions for better reliability")
    logging.debug("Secret key configured from environment")

    cors_origins = ["https://inmailer.vercel.app"]
    if os.getenv("FLASK_ENV") != "production":
        cors_origins.extend(
            [
                "http://localhost:3001",
                "http://127.0.0.1:3001",
            ]
        )

    CORS(
        app,
        supports_credentials=True,
        origins=cors_origins,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Set-Cookie"],
        max_age=3600,
    )

    @app.after_request
    def after_request(response):
        origin = request.headers.get("Origin")
        allowed_origins = ["https://inmailer.vercel.app"]
        if os.getenv("FLASK_ENV") != "production":
            allowed_origins.extend(
                [
                    "http://localhost:3001",
                    "http://127.0.0.1:3001",
                ]
            )
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    with app.app_context():
        initialize_callback()

    return app
