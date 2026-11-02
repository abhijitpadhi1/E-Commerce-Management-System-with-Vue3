import os

from app.extensions import db
from app.models import User
from app.utils.security import hash_password


def ensure_admin() -> None:
    admin_email: str = os.getenv("ADMIN_EMAIL").strip().lower()
    admin_name: str = os.getenv("ADMIN_NAME").strip()
    admin_password: str = os.getenv("ADMIN_PASSWORD")

    if not all([admin_email, admin_name, admin_password]):
        raise RuntimeError(
            "ADMIN_NAME, ADMIN_EMAIL, and ADMIN_PASSWORD must be configured in .env"
        )

    existing_user: User | None = User.query.filter_by(email=admin_email).first()
    if existing_user:
        if existing_user.role != "ADMIN":
            raise RuntimeError(
                f"Existing user {existing_user} has role {existing_user.role}"
            )
        print("Admin user already exists, skipping seed")
        return

    admin: User = User(
        name=admin_name,
        email=admin_email,
        password_hash=hash_password(admin_password),
        role="ADMIN",
        is_active=True,
    )

    db.session.add(admin)
    db.session.commit()

    print(f"Initial admin account created: {admin_email}")
