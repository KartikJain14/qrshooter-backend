from flask import request, jsonify
from models.role_model import Role
from models.user_model import User

def allocate_points():
    try:
        data = request.json
        
        # Extract the current user (who is allocating the points) and the target user
        current_user_id = data.get('current_user_id')  # ID of the user calling the function
        target_user_id = data.get('target_user_id')  # ID of the user receiving the points
        points = int(data.get('points'))  # Number of points to allocate

        # Fetch current user (the one performing the allocation)
        current_user = User.get_by_id(current_user_id)

        if not current_user:
            return jsonify({"error": "Current user not found"}), 404

        # Check if the current user has the proper role (SALES or ADMIN)
        if current_user.role not in [Role.SALES, Role.ADMIN]:
            return jsonify({"error": "Unauthorized: Only SALES or ADMIN can allocate points"}), 403

        # Ensure the user is not allocating points to themselves
        if current_user_id == target_user_id:
            return jsonify({"error": "You cannot allocate points to yourself"}), 400

        # Fetch target user
        target_user = User.get_by_id(target_user_id)

        if not target_user:
            return jsonify({"error": "Target user not found"}), 404
        
        if current_user.role == Role.SALES:
            if current_user.balance < points:
                return jsonify({"error": "Insufficient balance to allocate points"}), 400
            current_user.balance -= points
            current_user.save()

        # Allocate points to the target user
        target_user.update_credits(points, "ALLOCATE", current_user_id)  # Add points to the target user

        return jsonify({"message": f"Points successfully allocated to user {target_user_id}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def redeem_points():
    try:
        data = request.get_json()
        
        # Extract user ID and points to redeem
        current_user_id = data.get('current_user_id')  # User redeeming the points
        points = int(data.get('points'))  # Points to redeem

        # Fetch user from the database
        current_user = User.get_by_id(current_user_id)

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Ensure the user has enough credits
        current_credits = current_user.get_current_credits()
        if current_credits < points:
            return jsonify({"error": "Insufficient credits to redeem"}), 400

        # Redeem the points (deduct them from user's credits)
        current_user.update_credits(-points, "REDEEM", current_user_id)  # Deduct points

        return jsonify({"message": "Points redeemed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def transaction_history():
    try:
        data = request.get_json()
        
        # Extract user ID to fetch their transaction history
        user_id = data.get('user_id')

        # Fetch user from the database
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Return the transaction history
        return jsonify({"transaction_history": user.transaction_history}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def leaderboard():
    try:
        # Add limit parameter with default 50
        limit = request.args.get('limit', default=50, type=int)
        
        # Fetch users from database
        users = User.get_all()
        
        # Sort users by credits
        sorted_users = sorted(users, key=lambda x: x.credits, reverse=True)
        
        # Limit the number of users
        top_users = sorted_users[:limit]
        
        # Return only essential fields
        leaderboard_data = [{
            'first_name': user.first_name,
            'last_name': user.last_name,
            'credits': user.credits,
            'referral_code': user.referral_code
        } for user in top_users]
        
        return jsonify({
            "leaderboard": leaderboard_data,
            "total_users": len(sorted_users)
        }), 200

    except Exception as e:
        print(f"Leaderboard Error: {str(e)}")  # Debug log
        return jsonify({"error": "Failed to fetch leaderboard"}), 500