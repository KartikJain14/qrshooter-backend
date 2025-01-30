from flask import Blueprint
from controllers.auth_controller import (
    send_verification_code, 
    verify_code, 
    create_user_by_token, 
    search_user_by_email, 
    search_user_by_phone
    )
    

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/phone/auth', methods=['POST'])
def send_verification_code_route():
    return send_verification_code()

@auth_routes.route('/phone/verify_code', methods=['POST'])
def verify_code_route():
    return verify_code()

@auth_routes.route('/phone/add_user', methods=['POST'])
def add_user_route():
    return create_user_by_token()

@auth_routes.route('/user/by_email', methods=['POST'])
def search_user_by_email_route():
    return search_user_by_email()

@auth_routes.route('/user/by_phone', methods=['POST'])
def search_user_by_phone_route():
    return search_user_by_phone()