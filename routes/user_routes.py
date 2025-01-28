from flask import Blueprint
from controllers.user_controller import (
    add_user, 
    update_profile, 
    delete_profile, 
    get_profile
    )

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/add', methods=['POST'])
def add_user_route():
    return add_user()

@user_routes.route('/update', methods=['PUT'])
def update_profile_route():
    return update_profile()

@user_routes.route('/delete', methods=['DELETE'])
def delete_profile_route():
    return delete_profile()

@user_routes.route('/profile/<string:unique_id>', methods=['GET'])
def get_profile_route(unique_id):
    return get_profile(unique_id)