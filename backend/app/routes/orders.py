from decimal import Decimal
from typing import Any
from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Cart, CartItem, Order, OrderItem, Product
from app.services.offers import get_best_offer
from app.utils.decorators import role_required

orders_bp: Blueprint = Blueprint("orders", __name__, url_prefix="/orders")


def serialize_order(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "subtotal": str(order.subtotal),
        "discount_amount": str(order.discount_amount),
        "offer_code": order.offer_code,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "payment_status": order.payment_status,
        "shipping_address": order.shipping_address,
        "created_at": (order.created_at.isoformat() if order.created_at else None),
        "items": [
            {
                "product_id": item.product_id,
                "name": item.product_name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "sub_total": str(item.sub_total),
            }
            for item in order.items
        ],
    }


@orders_bp.get("/")
@role_required("CUSTOMER")
def get_my_orders() -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())

    orders: list[Order] = (
        Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    )

    return jsonify({"orders": [serialize_order(order) for order in orders]}), 200


@orders_bp.post("/checkout")
@role_required("CUSTOMER")
def checkout() -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())
    data: dict = request.get_json(silent=True) or {}

    shipping_address: str = data.get("shipping_address", "").strip()
    if not shipping_address:
        return jsonify({"message": "Shipping address is required."}), 400

    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({"message": "Your cart is empty."}), 400

    try:
        order_items: list[dict[str, Any]] = []
        offer_cart_items: list[dict[str, Any]] = []
        order_subtotal: Decimal = Decimal("0.00")

        for cart_item in cart.items:
            product: Product | None = (
                Product.query.filter_by(id=cart_item.product_id, is_active=True)
                .with_for_update()
                .first()
            )
            if not product:
                db.session.rollback()
                return (
                    jsonify(
                        {"message": "One or more products are no longer available."}
                    ),
                    400,
                )

            if cart_item.quantity > product.stock:
                db.session.rollback()
                return (
                    jsonify({"message": f"Insufficient stock for {product.name}."}),
                    400,
                )

            unit_price: Decimal = Decimal(str(product.price))
            item_subtotal: Decimal = unit_price * cart_item.quantity
            order_subtotal += item_subtotal

            # Preserve the original order-item price snapshot.
            order_items.append(
                {
                    "product": product,
                    "product_name": product.name,
                    "unit_price": unit_price,
                    "quantity": cart_item.quantity,
                    "sub_total": item_subtotal,
                }
            )

            # Input expected by the offer engine.
            offer_cart_items.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "unit_price": unit_price,
                    "quantity": cart_item.quantity,
                }
            )

        # Evaluate all eligible offers and select the best one.
        offer_result: dict[str, Any] = get_best_offer(offer_cart_items, order_subtotal)

        applied_offer: dict[str, Any] | None = offer_result["applied_offer"]
        discount_amount: Decimal = offer_result["discount_amount"]
        final_total: Decimal = offer_result["final_subtotal"]

        order: Order = Order(
            user_id=user_id,
            subtotal=order_subtotal,
            discount_amount=discount_amount,
            offer_code=(applied_offer["code"] if applied_offer else None),
            total_amount=final_total,
            status="PENDING_PAYMENT",
            payment_status="PENDING",
            shipping_address=shipping_address,
        )

        db.session.add(order)
        db.session.flush()

        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product"].id,
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                sub_total=item["sub_total"],
            )

            db.session.add(order_item)

        # Clear the cart only after the order has been created.
        cart.items.clear()
        db.session.commit()

        response = {
            "message": "Order created successfully.",
            "order": serialize_order(order),
            "offer": {
                "applied": applied_offer is not None,
                "code": applied_offer["code"] if applied_offer else None,
                "name": applied_offer["name"] if applied_offer else None,
                "discount_amount": str(discount_amount),
            },
        }

        return jsonify(response), 201

    except SQLAlchemyError:
        db.session.rollback()

        return (
            jsonify({"message": "Unable to create your order. Please try again."}),
            500,
        )


@orders_bp.get("/<int:order_id>")
@role_required("CUSTOMER")
def get_order(order_id: int) -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())

    order: Order | None = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        return jsonify({"message": "Order not found."}), 404

    return jsonify({"order": serialize_order(order)}), 200


@orders_bp.post("/<int:order_id>/modify")
@role_required("CUSTOMER")
def modify_unpaid_order(order_id: int) -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())

    # 1. Find the order belonging to this customer.
    order: Order | None = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if order is None:
        return (
            jsonify(
                {
                    "message": "Order not found.",
                }
            ),
            404,
        )

    # 2. Only unpaid, pending orders can be modified.
    if order.status != "PENDING_PAYMENT" or order.payment_status != "PENDING":
        return jsonify({"message": "Only unpaid orders can be modified."}), 409

    # 3. Get or create the customer's cart.
    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()

    unavailable_items = []

    try:
        # 4. Restore available order items to the cart.
        for order_item in order.items:
            product: Product | None = Product.query.filter_by(
                id=order_item.product_id, is_active=True
            ).first()
            if product is None:
                unavailable_items.append(
                    {
                        "product_id": order_item.product_id,
                        "product_name": order_item.product_name,
                        "quantity": order_item.quantity,
                        "message": "This product is no longer available.",
                    }
                )
                continue

            cart_item: CartItem | None = CartItem.query.filter_by(
                cart_id=cart.id, product_id=product.id
            ).first()
            if cart_item:
                cart_item.quantity += order_item.quantity
            else:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=order_item.quantity,
                )
                db.session.add(cart_item)

        # 5. Cancel the original unpaid order.
        order.status = "CANCELLED"

        # 6. Commit cart restoration and order cancellation together.
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to restore unpaid order %s to cart", order_id
        )
        return (
            jsonify({"message": "Unable to modify this order. Please try again."}),
            500,
        )

    return (
        jsonify(
            {
                "message": "Unpaid order cancelled and available items restored to cart.",
                "order_id": order.id,
                "order_status": order.status,
                "unavailable_items": unavailable_items,
            }
        ),
        200,
    )


@orders_bp.patch("/<int:order_id>/confirm-delivery")
@role_required("CUSTOMER")
def confirm_delivery(order_id: int) -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())
    order: Order | None = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"message": "Order not found."}), 404
    if order.status != "SHIPPED":
        return (
            jsonify({"message": "Only shipped orders can be marked as delivered."}),
            409,
        )

    order.status = "DELIVERED"
    order.delivered_at = db.func.now()

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Delivery confirmed successfully.",
                "order": serialize_order(order),
            }
        ),
        200,
    )


@orders_bp.get("/admin")
@role_required("ADMIN")
def get_all_orders() -> tuple[Response, int]:
    orders: list[Order] = Order.query.order_by(Order.created_at.desc()).all()

    return jsonify({"orders": [serialize_order(order) for order in orders]}), 200


@orders_bp.patch("/<int:order_id>/ship")
@role_required("ADMIN")
def ship_order(order_id: int) -> tuple[Response, int]:
    order: Order | None = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found."}), 404
    if order.payment_status != "PAID":
        return jsonify({"message": "Only paid orders can be shipped."}), 400
    if order.status != "PROCESSING":
        return jsonify({"message": "Only processing orders can be shipped."}), 409

    order.status = "SHIPPED"
    order.shipped_at = db.func.now()

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Order marked as shipped.",
                "order": serialize_order(order),
            }
        ),
        200,
    )
