import uuid
from flask import Blueprint, jsonify, request, Response
from flask import current_app
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Order, OrderItem, Product, Payment
from app.utils.decorators import role_required

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def validate_and_deduct_stock(order):
    """
    Validate that every ordered product has sufficient stock,
    then deduct the quantities.
    """

    # First validate every item.
    for item in order.items:
        product = (
            Product.query.filter_by(id=item.product_id, is_active=True)
            .with_for_update()
            .first()
        )
        if product is None:
            raise ValueError(f"Product '{item.product_name}' is no longer available.")
        if product.stock < item.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. Available: {product.stock}, requested: {item.quantity}."
            )

    # Only deduct after all items pass validation.
    for item in order.items:
        product = (
            Product.query.filter_by(id=item.product_id, is_active=True)
            .with_for_update()
            .first()
        )
        product.stock -= item.quantity


@payments_bp.post("/mock/<int:order_id>")
@role_required("CUSTOMER")
def mock_payment(order_id: int) -> Response:
    user_id: int = int(get_jwt_identity())
    data: dict = request.get_json(silent=True) or {}

    outcome: str = data.get("outcome", "success").lower()
    if outcome not in {"success", "failure"}:
        return jsonify({"message": "Outcome must be 'success' or 'failure'."}), 400

    order: Order | None = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"message": "Order not found."}), 404
    if order.payment_status == "PAID":
        return jsonify({"message": "This order has already been paid."}, 409)
    if order.status != "PENDING_PAYMENT":
        return jsonify({"message": "This order is not awaiting payment."}, 409)

    payment_status: str = "SUCCESS" if outcome == "success" else "FAILED"
    payment: Payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method="MOCK",
        payment_status=payment_status,
        transaction_reference=f"MOCK-{uuid.uuid4().hex[:12].upper()}",
    )

    try:
        db.session.add(payment)

        if outcome == "success":
            try:
                validate_and_deduct_stock(order)

                payment.payment_status = "SUCCESS"
                order.payment_status = "PAID"
                order.status = "PROCESSING"

                db.session.commit()

            except ValueError as error:
                db.session.rollback()

                payment.payment_status = "FAILED"
                payment.transaction_reference = None

                db.session.commit()

                return (
                    jsonify(
                        {
                            "message": str(error),
                            "payment_status": "FAILED",
                            "order_status": order.status,
                        }
                    ),
                    409,
                )

        db.session.commit()

        return (
            jsonify(
                {
                    "message": (
                        "Mock payment successful."
                        if outcome == "success"
                        else "Mock payment failed. You may try again."
                    ),
                    "payment": {
                        "order_id": payment.order_id,
                        "amount": str(payment.amount),
                        "payment_method": payment.payment_method,
                        "payment_status": payment.payment_status,
                        "transaction_reference": payment.transaction_reference,
                    },
                    "order": {
                        "id": order.id,
                        "status": order.status,
                        "payment_status": order.payment_status,
                    },
                }
            ),
            200,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Mock payment processing failed")
        return jsonify({"message": "Unable to process mock payment."}), 500
