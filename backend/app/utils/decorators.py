from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import User


def role_required(*allowed_roles):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            # Verify that the request has a valid JWT
            verify_jwt_in_request()

            # Get the user ID stored as the JWT identity
            user_id = get_jwt_identity()

            user = db.session.get(User, int(user_id))

            if not user:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "User account not found.",
                        }
                    ),
                    404,
                )

            if not user.is_active:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "This account is inactive.",
                        }
                    ),
                    403,
                )

            if user.role not in allowed_roles:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "You do not have permission to access this resource.",
                        }
                    ),
                    403,
                )

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator
