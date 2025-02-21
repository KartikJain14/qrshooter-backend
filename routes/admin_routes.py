from flask import Blueprint, request
from operator import itemgetter
from controllers.admin_controller import (
    auth_middleware,
    get_all_users, 
    update_user_points, 
    add_user, 
    remove_user,
    change_user_role
)

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.before_request
def check_auth():
    auth = auth_middleware(request.headers.get('TOKEN'))
    if auth:
        return auth

@admin_routes.route('/users', methods=['GET'])
def get_all_users_route():
    sort_order = request.args.get("sort", "ascending")
    users = get_all_users()
    if sort_order == "descending":
        users.sort(key=itemgetter("credits"), reverse=True)
    else:
        users.sort(key=itemgetter("credits"))
    return users

@admin_routes.route('/points/update', methods=['PUT'])
def update_user_points_route():
    data = request.json
    user_id = data.get('user_id')
    points = data.get('points')
    return update_user_points(user_id, points)

@admin_routes.route('/users/add', methods=['POST'])
def add_user_route():
    data = request.json
    return add_user(data)

@admin_routes.route('/users/<string:user_id>', methods=['DELETE'])
def remove_user_route(user_id):
    return remove_user(user_id)

@admin_routes.route('/users/role', methods=['PUT'])
def change_role_route():
    data = request.json
    admin_id = data.get('admin_id')
    target_user_id = data.get('user_id')
    new_role = data.get('role')
    return change_user_role(admin_id, target_user_id, new_role)