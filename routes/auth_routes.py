from flask import Blueprint



auth_routes = Blueprint('auth_routes', __name__)

# Import and register the routes from their respective files
from routes.register import register, reset_registration
from routes.verify import verify_code, resend_code
from routes.pin import save_pin
from routes.validate_session import validate_session
from routes.password_reset import auth_password_reset
from routes.get_salt import get_salt
from routes.account_freeze import account_freeze
from routes.store_public_key import store_public_key
from routes.check_public_key import check_public_key
from routes.login import login
from routes.send_report import send_report

auth_routes.add_url_rule('/register', view_func=register, methods=['POST'])
auth_routes.add_url_rule('/register/reset', view_func=reset_registration, methods=['POST'])
auth_routes.add_url_rule('/verify_code', view_func=verify_code, methods=['POST'])
auth_routes.add_url_rule('/resend_code', view_func=resend_code, methods=['POST'])
auth_routes.add_url_rule('/verify_pin', view_func=save_pin, methods=['POST'])
auth_routes.add_url_rule('/login', view_func=login, methods=['POST'])
auth_routes.add_url_rule('/validate_session', view_func=validate_session, methods=['POST'])
auth_routes.add_url_rule('/password_reset', view_func=auth_password_reset, methods=['POST'])
auth_routes.add_url_rule('/get_salt', view_func=get_salt, methods=['POST'])
auth_routes.add_url_rule('/account_freeze', view_func=account_freeze, methods=['POST'])
auth_routes.add_url_rule('/store_public_key', view_func=store_public_key, methods=['POST'])
auth_routes.add_url_rule('/check_public_key', view_func=check_public_key, methods=['POST'])
auth_routes.add_url_rule('/send_report', view_func=send_report, methods=['POST'])
