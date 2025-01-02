from flask import Blueprint, request
from controllers.admin_controller import (
    get_all_users, 
    update_user_points, 
    add_user, 
    remove_user,
    change_user_role
)

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin/users', methods=['GET'])
def get_all_users_route():
    return get_all_users()

@admin_routes.route('/admin/points/update', methods=['PUT'])
def update_user_points_route():
    data = request.json
    user_id = data.get('user_id')
    points = data.get('points')
    return update_user_points(user_id, points)

@admin_routes.route('/admin/users/add', methods=['POST'])
def add_user_route():
    data = request.json
    return add_user(data)

@admin_routes.route('/admin/users/<string:user_id>', methods=['DELETE'])
def remove_user_route(user_id):
    return remove_user(user_id)

@admin_routes.route('/admin/users/role', methods=['PUT'])
def change_role_route():
    data = request.json
    admin_id = data.get('admin_id')
    target_user_id = data.get('user_id')
    new_role = data.get('role')
    return change_user_role(admin_id, target_user_id, new_role)