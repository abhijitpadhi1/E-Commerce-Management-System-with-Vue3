import logging
import requests
from decimal import Decimal, InvalidOperation

from app import create_app
from app.extensions import db
from app.models import Product

API_URL = "https://fakestoreapi.com/products"
DEFAULT_STOCK = 20

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fetch_products() -> list[dict]:
    """Fetch sample products from Fake Store API."""
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()

        products = response.json()

        if not isinstance(products, list):
            raise ValueError("API response was not a list of products.")

        return products

    except requests.RequestException as error:
        logging.error("Could not fetch products: %s", error)
        raise


def map_product(api_product: dict) -> dict:
    """Convert an API product into our database model fields."""
    try:
        price = Decimal(str(api_product["price"]))
    except (KeyError, InvalidOperation, TypeError) as error:
        raise ValueError("Product has an invalid price.") from error

    if price < 0:
        raise ValueError("Product price cannot be negative.")

    name = str(api_product.get("title", "")).strip()
    description = str(api_product.get("description", "")).strip()
    category = str(api_product.get("category", "Uncategorized")).strip()
    image_url = str(api_product.get("image", "")).strip()

    if not name:
        raise ValueError("Product is missing a title.")

    return {
        "name": name,
        "description": description,
        "price": price,
        "stock": DEFAULT_STOCK,
        "category": category or "Uncategorized",
        "image_url": image_url or None,
        "is_active": True,
    }


def seed_products() -> None:
    """Insert API products without modifying existing products."""
    products = fetch_products()

    added_count = 0
    skipped_count = 0
    failed_count = 0

    for api_product in products:
        try:
            product_data = map_product(api_product)

            # Avoid inserting duplicate products by name.
            existing_product = (
                db.session.query(Product).filter_by(name=product_data["name"]).first()
            )

            if existing_product:
                logging.info("Skipping existing product: %s", product_data["name"])
                skipped_count += 1
                continue

            product = Product(**product_data)
            db.session.add(product)
            added_count += 1

        except (ValueError, KeyError, TypeError) as error:
            logging.warning(
                "Skipping invalid API product: %s",
                error,
            )
            failed_count += 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logging.exception("Database commit failed.")
        raise

    logging.info("Product seeding completed.")
    logging.info("Added: %s", added_count)
    logging.info("Skipped existing: %s", skipped_count)
    logging.info("Invalid products: %s", failed_count)


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        seed_products()
