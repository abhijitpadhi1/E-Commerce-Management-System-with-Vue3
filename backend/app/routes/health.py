from flask import Blueprint, Response, jsonify

health_bp: Blueprint = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check() -> tuple[Response, int]:
    return (
        jsonify({"status": "success", "message": "E-commerce backend is running"}),
        200,
    )
