from datetime import datetime, timezone

from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    offer_code = db.Column(db.String(50), nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="PENDING")
    payment_status = db.Column(db.String(50), nullable=False, default="UNPAID")
    shipping_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    shiped_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="orders", lazy=True)
    items = db.relationship(
        "OrderItem", back_populates="order", lazy=True, cascade="all, delete-orphan"
    )
    payments = db.relationship(
        "Payment", back_populates="order", lazy=True, cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        db.CheckConstraint("total_amount > 0", name="check_total_positive"),
    )

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id} status={self.status}>"
