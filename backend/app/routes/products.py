from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request, Response
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Product
from app.utils.decorators import role_required

product_bp: Blueprint = Blueprint("products", __name__, url_prefix="/products")


def serialize_product(product: Product) -> dict:
    """Convert a Product model instance into JSON-safe data."""
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "category": product.category,
        "image_url": product.image_url,
        "is_active": product.is_active,
        "created_at": (product.created_at.isoformat() if product.created_at else None),
        "updated_at": (product.updated_at.isoformat() if product.updated_at else None),
    }


def validate_product_data(data: dict, partial: bool = False) -> dict:
    """
    Validate product fields.

    partial=False: all required fields must be present.
    partial=True: validate only fields supplied for PATCH.
    """
    errors: dict[str, str] = {}
    allowed_fields = {
        "name",
        "description",
        "price",
        "stock",
        "category",
        "image_url",
    }

    unknown_fields: set[str] = set(data.keys()) - allowed_fields
    if unknown_fields:
        errors["unknown_fields"] = (
            f"Unsupported fields: {', '.join(sorted(unknown_fields))}"
        )

    required_fields: set[str] = {"name", "price", "stock", "category"}
    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = "This field is required."

    # Validate text fields
    for field in ("name", "category"):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                errors[field] = "Must be a non-empty string."

    for field in ("description", "image_url"):
        if field in data and data[field] is not None:
            if not isinstance(data[field], str):
                errors[field] = "Must be a string."

    # Validate price
    if "price" in data:
        try:
            price: Decimal = Decimal(str(data["price"]))
            if not price.is_finite() or price < 0:
                errors["price"] = "Must be a valid non-negative number."
        except (InvalidOperation, ValueError, TypeError):
            errors["price"] = "Must be a valid number."

    # Validate stock
    if "stock" in data:
        stock: Any = data["stock"]
        # bool is a subclass of int in Python, so reject it explicitly.
        if isinstance(stock, bool) or not isinstance(stock, int):
            errors["stock"] = "Must be an integer."
        elif stock < 0:
            errors["stock"] = "Cannot be negative."

    return errors


@product_bp.post("/")
@role_required("ADMIN")
def create_product() -> tuple[Response, int]:
    data: Any = request.get_json(silent=True)
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

    errors: dict[str, str] = validate_product_data(data)
    if errors:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product validation failed.",
                    "errors": errors,
                }
            ),
            400,
        )

    try:
        product: Product = Product(
            name=data["name"].strip(),
            description=data.get("description"),
            price=Decimal(str(data["price"])),
            stock=data["stock"],
            category=data["category"].strip(),
            image_url=data.get("image_url"),
            is_active=True,
        )

        db.session.add(product)
        db.session.commit()

    except (InvalidOperation, ValueError, TypeError):
        db.session.rollback()

        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid product data.",
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "status": "success",
                "message": "Product created successfully.",
                "product": serialize_product(product),
            }
        ),
        201,
    )


@product_bp.get("/")
def get_products() -> tuple[Response, int]:
    # Public catalogue: only active products are visible.
    products = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .all()
    )
    return (
        jsonify(
            {
                "status": "success",
                "count": len(products),
                "products": [serialize_product(product) for product in products],
            }
        ),
        200,
    )


@product_bp.get("/<int:product_id>")
def get_product(product_id: int) -> tuple[Response, int]:
    product: Product | None = Product.query.filter_by(
        id=product_id, is_active=True
    ).first()
    if not product:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product not found.",
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "status": "success",
                "product": serialize_product(product),
            }
        ),
        200,
    )


@product_bp.patch("/<int:product_id>")
@role_required("ADMIN")
def update_product(product_id: int) -> tuple[Response, int]:
    product: Product | None = db.session.get(Product, product_id)
    if not product:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product not found.",
                }
            ),
            404,
        )

    data: Any = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Request body must be a non-empty JSON object.",
                }
            ),
            400,
        )

    errors: dict[str, str] = validate_product_data(data, partial=True)
    if errors:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product validation failed.",
                    "errors": errors,
                }
            ),
            400,
        )

    try:
        if "name" in data:
            product.name = data["name"].strip()

        if "description" in data:
            product.description = data["description"]

        if "price" in data:
            product.price = Decimal(str(data["price"]))

        if "stock" in data:
            product.stock = data["stock"]

        if "category" in data:
            product.category = data["category"].strip()

        if "image_url" in data:
            product.image_url = data["image_url"]

        db.session.commit()

    except (InvalidOperation, ValueError, TypeError):
        db.session.rollback()
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid product data.",
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "status": "success",
                "message": "Product updated successfully.",
                "product": serialize_product(product),
            }
        ),
        200,
    )


@product_bp.delete("/<int:product_id>")
@role_required("ADMIN")
def delete_product(product_id: int) -> tuple[Response, int]:
    product: Product | None = db.session.get(Product, product_id)
    if not product:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Product not found.",
                }
            ),
            404,
        )

    product.is_active = False
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "message": "Product deactivated successfully.",
            }
        ),
        200,
    )


@product_bp.get("/admin")
@role_required("ADMIN")
def get_all_products_admin() -> tuple[Response, int]:
    products: list[Product] = Product.query.order_by(Product.created_at.desc()).all()

    return (
        jsonify(
            {
                "status": "success",
                "count": len(products),
                "products": [serialize_product(product) for product in products],
            }
        ),
        200,
    )
