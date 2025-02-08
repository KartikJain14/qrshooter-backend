from flask import Blueprint, jsonify
from controllers.credit_controller import (
    allocate_points, 
    redeem_points, 
    transaction_history, 
    leaderboard
    )

credit_routes = Blueprint('credit_routes', __name__)

# Route to allocate points to a user
@credit_routes.route('/points/allocate', methods=['POST'])
def allocate_points_route():
    return allocate_points()

# Route to redeem points from a user
@credit_routes.route('/points/redeem', methods=['POST'])
def redeem_points_route():
    return redeem_points()

# Route to get transaction history of a user
@credit_routes.route('/transactions/history', methods=['POST'])
def transaction_history_route():
    return transaction_history()

@credit_routes.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        return leaderboard()
    except Exception as e:
        print(f"Route Error: {str(e)}")  # Debug log
        return jsonify({"error": "Server timeout"}), 504