from pathlib import Path

from celery.result import AsyncResult
from flask import Blueprint, jsonify, request, Response, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.tasks.export_tasks import export_customer_order_history
from app.utils.decorators import role_required
from app.extensions import celery

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")

EXPORT_DIR = Path(__file__).resolve().parents[2] / "generated_exports"


@exports_bp.post("/orders")
@role_required("CUSTOMER")
def start_order_export() -> tuple[Response, int]:
    customer_id: int = int(get_jwt_identity())

    data: dict[str, Any] = request.get_json(silent=True) or {}
    export_format = data.get("format", "csv").lower()

    if export_format not in {"csv", "xlsx"}:
        return jsonify({"error": "Format must be either 'csv' or 'xlsx'."}), 400

    task = export_customer_order_history.delay(customer_id, export_format)

    return (
        jsonify(
            {
                "message": "Your order history export has been queued.",
                "task_id": task.id,
                "status": "PENDING",
                "format": export_format,
            }
        ),
        202,
    )


@exports_bp.get("/orders/<task_id>/status")
@role_required("CUSTOMER")
def order_export_status(task_id: str) -> tuple[Response, int]:
    customer_id: int = int(get_jwt_identity())

    task = AsyncResult(task_id, app=celery)
    if task.state == "SUCCESS":
        result: dict[str, Any] = task.result

        # Ensure the completed export belongs to this customer.
        if result.get("customer_id") != customer_id:
            return jsonify({"error": "Export not found."}), 404

        return jsonify(
            {
                "task_id": task_id,
                "status": task.state,
                "order_count": result["order_count"],
                "format": result["export_format"],
                "email_sent": result["email_sent"],
            }
        )

    if task.state == "FAILURE":
        return (
            jsonify(
                {
                    "task_id": task_id,
                    "status": task.state,
                    "error": "Export generation failed.",
                }
            ),
            500,
        )

    return jsonify(
        {
            "task_id": task_id,
            "status": task.state,
        }
    )


@exports_bp.get("/orders/<task_id>/download")
@role_required("CUSTOMER")
def download_order_export(task_id: int) -> tuple[Response, int]:
    customer_id: int = int(get_jwt_identity())

    task = AsyncResult(task_id, app=celery)
    if task.state != "SUCCESS":
        return jsonify({"error": "Export is not ready."}), 409

    result = task.result
    if result.get("customer_id") != customer_id:
        return jsonify({"error": "Export not found."}), 404

    filename = result.get("filename")
    if not filename:
        return jsonify({"error": "Export file not found."}), 404

    file_path = EXPORT_DIR / filename
    if not file_path.is_file():
        return jsonify({"error": "Export file no longer exists."}), 404

    return send_from_directory(
        EXPORT_DIR,
        filename,
        as_attachment=True,
        mimetype="text/csv",
    )
