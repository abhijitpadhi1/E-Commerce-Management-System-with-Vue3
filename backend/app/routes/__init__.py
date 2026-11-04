from flask import Blueprint

from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.products import product_bp
from app.routes.cart import cart_bp
from app.routes.orders import orders_bp
from app.routes.payments import payments_bp
from app.routes.admindashboard import dashboard_bp
from app.routes.exports import exports_bp

api_bp: Blueprint = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(product_bp)
api_bp.register_blueprint(cart_bp)
api_bp.register_blueprint(orders_bp)
api_bp.register_blueprint(payments_bp)
api_bp.register_blueprint(dashboard_bp)
api_bp.register_blueprint(exports_bp)
