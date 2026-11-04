from flask import Flask

from app import models
from app.config import Config
from app.extensions import db, jwt, cors, celery, mail, cache
from app.routes import api_bp
from app.utils.seed import ensure_admin


def create_app() -> Flask:
    # Create the flask application
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure celery
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_track_started=True,
        task_time_limit=30 * 60,
    )
    celery.flask_app = app

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    mail.init_app(app)
    cache.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Setup database tables and seed admin user
    with app.app_context():
        db.create_all()
        ensure_admin()

    return app
