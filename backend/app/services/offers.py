from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")


OFFERS = [
    # Type 1: Percentage discount based on cart subtotal
    {
        "code": "SAVE10",
        "name": "10% off orders above ₹1,000",
        "type": "percentage",
        "minimum_subtotal": Decimal("1000.00"),
        "discount_percent": Decimal("10"),
    },
    {
        "code": "SAVE15",
        "name": "15% off orders above ₹1,500",
        "type": "percentage",
        "minimum_subtotal": Decimal("1500.00"),
        "discount_percent": Decimal("15"),
    },
    {
        "code": "SAVE25",
        "name": "25% off orders above ₹2,500",
        "type": "percentage",
        "minimum_subtotal": Decimal("2500.00"),
        "discount_percent": Decimal("25"),
    },
    # Type 2: Fixed amount discount
    {
        "code": "FLAT100",
        "name": "₹100 off orders above ₹1,000",
        "type": "fixed",
        "minimum_subtotal": Decimal("1000.00"),
        "discount_amount": Decimal("100.00"),
    },
    {
        "code": "FLAT300",
        "name": "₹300 off orders above ₹2,000",
        "type": "fixed",
        "minimum_subtotal": Decimal("2000.00"),
        "discount_amount": Decimal("300.00"),
    },
    # Type 3: Category-specific percentage discount
    {
        "code": "TECH20",
        "name": "20% off Electronics",
        "type": "category_percentage",
        "category": "Electronics",
        "discount_percent": Decimal("20"),
    },
    {
        "code": "ACCESS15",
        "name": "15% off Accessories",
        "type": "category_percentage",
        "category": "Accessories",
        "discount_percent": Decimal("15"),
    },
    # Type 4: Quantity-based discount
    {
        "code": "BULK10",
        "name": "10% off when buying 3 or more items",
        "type": "quantity_percentage",
        "minimum_quantity": 3,
        "discount_percent": Decimal("10"),
    },
    {
        "code": "BULK15",
        "name": "15% off when buying 5 or more items",
        "type": "quantity_percentage",
        "minimum_quantity": 5,
        "discount_percent": Decimal("15"),
    },
    # Type 5: Buy X, Get Y
    {
        "code": "BUY2GET1",
        "name": "Buy 2, get 1 free on the same product",
        "type": "buy_x_get_y",
        "buy_quantity": 2,
        "free_quantity": 1,
    },
]


def money(value: Decimal) -> Decimal:
    """Round a monetary value to two decimal places."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_offer_discount(
    offer: dict, cart_items: list[dict], subtotal: Decimal
) -> Decimal:
    """
    Calculate the discount for one offer.

    Expected cart item format:
    {
        "product_id": 1,
        "name": "Product name",
        "category": "Electronics",
        "unit_price": Decimal("500.00"),
        "quantity": 2,
    }
    """

    subtotal = Decimal(str(subtotal))

    offer_type = offer["type"]
    if offer_type == "percentage":
        if subtotal < offer["minimum_subtotal"]:
            return Decimal("0.00")
        discount = subtotal * offer["discount_percent"] / Decimal("100")
    elif offer_type == "fixed":
        if subtotal < offer["minimum_subtotal"]:
            return Decimal("0.00")
        discount = offer["discount_amount"]
    elif offer_type == "category_percentage":
        eligible_subtotal = sum(
            (
                Decimal(str(item["unit_price"])) * item["quantity"]
                for item in cart_items
                if item["category"].lower() == offer["category"].lower()
            ),
            Decimal("0.00"),
        )
        discount = eligible_subtotal * offer["discount_percent"] / Decimal("100")
    elif offer_type == "quantity_percentage":
        total_quantity = sum(item["quantity"] for item in cart_items)
        if total_quantity < offer["minimum_quantity"]:
            return Decimal("0.00")
        discount = subtotal * offer["discount_percent"] / Decimal("100")
    elif offer_type == "buy_x_get_y":
        buy_quantity = offer["buy_quantity"]
        free_quantity = offer["free_quantity"]
        discount = Decimal("0.00")
        for item in cart_items:
            quantity = item["quantity"]
            free_items = (quantity // (buy_quantity + free_quantity)) * free_quantity
            if free_items > 0:
                unit_price = Decimal(str(item["unit_price"]))
                discount += unit_price * free_items
    else:
        return Decimal("0.00")

    # A discount must never exceed the subtotal.
    return min(money(discount), money(subtotal))


def get_best_offer(cart_items: list[dict], subtotal: Decimal) -> dict:
    """
    Evaluate every offer and return only the best eligible offer.
    Offers are not stacked.
    """
    subtotal = money(Decimal(str(subtotal)))
    best_offer = None
    best_discount = Decimal("0.00")
    for offer in OFFERS:
        discount = calculate_offer_discount(
            offer=offer, cart_items=cart_items, subtotal=subtotal
        )
        if discount > best_discount:
            best_offer = offer
            best_discount = discount
    final_subtotal = money(subtotal - best_discount)

    return {
        "applied_offer": best_offer,
        "discount_amount": best_discount,
        "subtotal": subtotal,
        "final_subtotal": final_subtotal,
    }
