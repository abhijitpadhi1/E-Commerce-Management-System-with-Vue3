from app.extensions import db


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    # Product details captured at purchase time
    product_name = db.Column(db.String(150), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sub_total = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    order = db.relationship("Order", back_populates="items", lazy=True)
    product = db.relationship("Product", back_populates="order_items", lazy=True)

    # Table Constraints
    __table_args__ = (
        db.UniqueConstraint("order_id", "product_id", name="uq_order_product"),
        db.CheckConstraint("quantity > 0", name="check_quantity_positive"),
        db.CheckConstraint("unit_price > 0", name="check_price_positive"),
        db.CheckConstraint("sub_total > 0", name="check_sub_total_positive"),
    )

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id} product_id={self.product_id}>"
