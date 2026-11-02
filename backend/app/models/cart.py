from datetime import datetime, timezone
from app.extensions import db


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship("User", back_populates="cart", lazy=True)
    items = db.relationship(
        "CartItem", back_populates="cart", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id}>"
