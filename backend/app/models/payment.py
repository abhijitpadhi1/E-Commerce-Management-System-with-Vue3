from datetime import datetime, timezone

from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False, default="MOKE")
    payment_status = db.Column(db.String(20), nullable=False, default="PENDING")
    transaction_reference = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    order = db.relationship("Order", back_populates="payments", lazy=True)

    # Table Constraints
    __table_args__ = (db.CheckConstraint(amount > 0, name="check_amount_positive"),)

    def __repr__(self):
        return f"Payment order_id={self.order_id} status={self.payment_status}"
