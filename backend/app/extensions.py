from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery, Task


class FlaskContextTask(Task):
    """Run Celery tasks inside the Flask application context."""

    abstract = True

    def __call__(self, *args, **kwargs):
        flask_app = self.app.flask_app
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery: Celery = Celery("ecommerce", task_cls=FlaskContextTask)
db: SQLAlchemy = SQLAlchemy()
jwt: JWTManager = JWTManager()
cors: CORS = CORS()
mail: Mail = Mail()
cache: Cache = Cache()
