from flask import Blueprint, jsonify, request, Response
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User
from app.utils.security import hash_password, verify_password
from app.utils.decorators import role_required


auth_bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")


# Route to handle user signup
@auth_bp.post("/signup")
def signup() -> tuple[Response, int]:
    data: dict | None = request.get_json(silent=True)

    if not isinstance(data, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    name: str = data.get("name", "").strip()
    email: str = data.get("email", "").strip().lower()
    password: str = data.get("password", "")

    # Validate required fields
    if not name or not email or not password:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Name, email, and password are required.",
                }
            ),
            400,
        )

    # Basic email validation for this stage
    if "@" not in email or "." not in email.split("@")[-1]:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Please provide a valid email address.",
                }
            ),
            400,
        )

    if len(password) < 8:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Password must contain at least 8 characters.",
                }
            ),
            400,
        )

    # Check whether the email is already registered
    existing_user: User | None = User.query.filter_by(email=email).first()
    if existing_user:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An account with this email already exists.",
                }
            ),
            409,
        )

    # Create a customer account
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="CUSTOMER",
        is_active=True,
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        # Handles a duplicate email caused by simultaneous requests
        db.session.rollback()

        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An account with this email already exists.",
                }
            ),
            409,
        )

    return (
        jsonify(
            {
                "status": "success",
                "message": "Account created successfully.",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        ),
        201,
    )


# Route to handle user login
@auth_bp.post("/login")
def login() -> tuple[Response, int]:
    data: dict | None = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    email: str = data.get("email", "").strip().lower()
    password: str = data.get("password", "")
    if not email or not password:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Email and password are required.",
                }
            ),
            400,
        )

    user: User | None = User.query.filter_by(email=email).first()

    # Use a generic error message so we don't reveal whether an email is registered.
    if not user or not verify_password(password, user.password_hash):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid email or password.",
                }
            ),
            401,
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

    access_token: str = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
        },
    )

    return (
        jsonify(
            {
                "status": "success",
                "message": "Login successful.",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        ),
        200,
    )


# Route to get current user information
@auth_bp.get("/me")
@jwt_required()
def get_current_user() -> tuple[Response, int]:
    user_id: str = get_jwt_identity()
    user: User | None = db.session.get(User, int(user_id))
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

    return (
        jsonify(
            {
                "status": "success",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        ),
        200,
    )
