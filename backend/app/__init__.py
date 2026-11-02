from flask import Flask

from app import models
from app.config import Config
from app.extensions import db, jwt, cors
from app.routes import api_bp
from app.utils.seed import ensure_admin


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        ensure_admin()

    return app
