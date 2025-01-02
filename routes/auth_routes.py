from flask import Blueprint
from controllers.auth_controller import send_verification_code, verify_code, google_sign_in

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/auth/phone/send_code', methods=['POST'])
def send_verification_code_route():
    return send_verification_code()

@auth_routes.route('/auth/phone/verify_code', methods=['POST'])
def verify_code_route():
    return verify_code()

@auth_routes.route('/auth/google/sign_in', methods=['POST'])
def google_sign_in_route():
    return google_sign_in()