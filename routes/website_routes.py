from flask import Blueprint, request, render_template, jsonify
from controllers.website_controller import (
    index, admin_login, home, add_user_logic, user_details,
    update_user_points_logic, update_user_role_logic, delete_user_logic, get_user_transactions_logic
)
import os

website_routes = Blueprint('website_routes', __name__)

@website_routes.route("/", methods=["GET"])
@website_routes.route("/home", methods=["GET"])
def route_home():
    return home()

@website_routes.route("/admin/users/add", methods=["GET", "POST"])
def route_add_user():
    if request.method == "POST":
        return add_user_logic(request.json)
    return render_template("AddUser.html")

@website_routes.route("/user/<string:user_id>", methods=["GET"])
def route_user_details(user_id):
    return user_details(user_id)

@website_routes.route("/user/points/update", methods=["POST"])
def route_update_user_points():
    user_id = request.form.get('user_id')
    points = int(request.form.get('points', 0))
    return update_user_points_logic(user_id, points)

@website_routes.route("/user/role/update", methods=["POST"])
def route_update_user_role():
    user_id = request.form.get('user_id')
    new_role = request.form.get('role')
    return update_user_role_logic(user_id, new_role)

@website_routes.route("/user/delete", methods=["POST"])
def route_delete_user():
    user_id = request.form.get('user_id')
    return delete_user_logic(user_id)

@website_routes.route("/user/<string:user_id>/transactions", methods=["GET"])
def route_user_transactions(user_id):
    return get_user_transactions_logic(user_id)
