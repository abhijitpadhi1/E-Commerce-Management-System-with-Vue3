from app.extensions import db


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    cart = db.relationship("Cart", back_populates="items", lazy=True)
    product = db.relationship("Product", back_populates="cart_items", lazy=True)

    # Table Constraints
    __table_args__ = (
        db.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
        db.CheckConstraint("quantity > 0", name="check_quantity_positive"),
    )

    def __repr__(self):
        return f"<CartItem cart_id={self.cart_id} product_id={self.product_id} quantity={self.quantity}>"
