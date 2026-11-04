from decimal import Decimal
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Cart, CartItem, Product, User
from app.utils.decorators import role_required

cart_bp: Blueprint = Blueprint("cart", __name__, url_prefix="/cart")


def touch_cart(cart: Cart) -> None:
    cart.updated_at = datetime.now(timezone.utc)


def serialize_cart_item(cart_item: CartItem) -> dict:
    product: Product = cart_item.product
    unit_price: Decimal = product.price
    subtotal: Decimal = unit_price * cart_item.quantity

    return {
        "id": cart_item.id,
        "product_id": product.id,
        "quantity": cart_item.quantity,
        "unit_price": str(unit_price),
        "subtotal": str(subtotal),
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "image_url": product.image_url,
            "stock": product.stock,
            "is_active": product.is_active,
        },
    }


@cart_bp.get("/")
@role_required("CUSTOMER")
def get_cart() -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())
    user: User | None = db.session.get(User, user_id)
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

    cart: Cart | None = Cart.query.filter_by(user_id=user.id).first()
    # Create a cart automatically for a customer who does not have one.
    if not cart:
        cart: Cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()

    cart_items: list[dict] = []
    total_amount: Decimal = Decimal("0.00")
    total_quantity: int = 0
    for item in cart.items:
        serialized_item: dict = serialize_cart_item(item)
        cart_items.append(serialized_item)
        total_amount += item.product.price * item.quantity
        total_quantity += item.quantity
    return (
        jsonify(
            {
                "status": "success",
                "cart": {
                    "id": cart.id,
                    "items": cart_items,
                    "total_quantity": total_quantity,
                    "total_amount": str(total_amount),
                },
            }
        ),
        200,
    )


@cart_bp.post("/items")
@role_required("CUSTOMER")
def add_cart_item() -> tuple[Response, int]:
    data: dict | None = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must be a valid JSON object.",
                }
            ),
            400,
        )

    product_id: int | None = data.get("product_id")
    quantity: int | None = data.get("quantity", 1)

    # Validate product_id
    if isinstance(product_id, bool) or not isinstance(product_id, int):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "product_id must be an integer.",
                }
            ),
            400,
        )

    # Validate quantity
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "quantity must be an integer.",
                }
            ),
            400,
        )

    if quantity <= 0:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "quantity must be greater than zero.",
                }
            ),
            400,
        )

    # Find the product
    product: Product | None = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product not found or unavailable.",
                }
            ),
            404,
        )

    # Get or create the customer's cart
    user_id: int = int(get_jwt_identity())
    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()

    # Check whether this product is already in the cart
    cart_item: CartItem | None = CartItem.query.filter_by(
        cart_id=cart.id, product_id=product.id
    ).first()
    if cart_item:
        new_quantity: int = cart_item.quantity + quantity
    else:
        new_quantity: int = quantity

    # Validate the combined quantity against current stock
    if new_quantity > product.stock:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        f"Only {product.stock} unit(s) of this product "
                        "are currently available."
                    ),
                }
            ),
            400,
        )

    # Update existing item or create a new one
    if cart_item:
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        touch_cart(cart)
        db.session.add(cart_item)

    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Product added to cart successfully.",
                "cart_item": serialize_cart_item(cart_item),
            }
        ),
        201,
    )


@cart_bp.patch("/items/<int:item_id>")
@role_required("CUSTOMER")
def update_cart_item(item_id: int) -> tuple[Response, int]:
    data: dict | None = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must be a valid JSON object.",
                }
            ),
            400,
        )

    quantity: int | None = data.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "quantity must be an integer.",
                }
            ),
            400,
        )

    if quantity <= 0:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "quantity must be greater than zero.",
                }
            ),
            400,
        )

    user_id: int = int(get_jwt_identity())
    # Find this customer's cart
    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Cart not found.",
                }
            ),
            404,
        )

    # Scope the item lookup to this customer's cart
    cart_item: CartItem | None = CartItem.query.filter_by(
        id=item_id, cart_id=cart.id
    ).first()
    if not cart_item:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Cart item not found.",
                }
            ),
            404,
        )

    product: Product = cart_item.product
    if not product.is_active:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "This product is no longer available.",
                }
            ),
            400,
        )

    if quantity > product.stock:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        f"Only {product.stock} unit(s) of this product "
                        "are currently available."
                    ),
                }
            ),
            400,
        )

    cart_item.quantity = quantity
    touch_cart(cart)
    db.session.commit()
    return (
        jsonify(
            {
                "status": "success",
                "message": "Cart item quantity updated successfully.",
                "cart_item": serialize_cart_item(cart_item),
            }
        ),
        200,
    )


@cart_bp.delete("/items/<int:item_id>")
@role_required("CUSTOMER")
def remove_cart_item(item_id: int) -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())
    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Cart not found.",
                }
            ),
            404,
        )

    cart_item: CartItem | None = CartItem.query.filter_by(
        id=item_id, cart_id=cart.id
    ).first()
    if not cart_item:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Cart item not found.",
                }
            ),
            404,
        )

    db.session.delete(cart_item)
    touch_cart(cart)
    db.session.commit()
    return (
        jsonify(
            {
                "status": "success",
                "message": "Item removed from cart successfully.",
            }
        ),
        200,
    )


@cart_bp.delete("/")
@role_required("CUSTOMER")
def clear_cart() -> tuple[Response, int]:
    user_id: int = int(get_jwt_identity())
    cart: Cart | None = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Cart is already empty.",
                }
            ),
            200,
        )

    for item in cart.items:
        db.session.delete(item)
    touch_cart(cart)
    db.session.commit()
    return (
        jsonify(
            {
                "status": "success",
                "message": "Cart cleared successfully.",
            }
        ),
        200,
    )
