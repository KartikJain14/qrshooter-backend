from flask import request, jsonify
from models.role_model import Role
from models.user_model import User
from db import get_collection_reference, get_document_reference
import time
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
        limit = min(request.args.get('limit', default=10, type=int), 50)
        
        users_ref = get_collection_reference('users')
        leaderboard_ref = get_document_reference('cache', 'leaderboard')
        
        # Try to get cached leaderboard first
        cached_data = leaderboard_ref.get()
        
        if cached_data.exists:
            cache_dict = cached_data.to_dict()
            leaderboard_data = cache_dict.get('rankings', [])[:limit]
            last_updated = int(cache_dict.get('last_updated', 0))  # Ensure int
            
            # If data is fresh enough (less than 5 minutes old)
            if int(time.time()) - last_updated < 300:
                return jsonify({
                    "data": leaderboard_data,
                    "count": len(leaderboard_data),
                    "cached": True
                }), 200
        
        # If no cache or cache expired, get fresh data
        query = users_ref.order_by('credits', direction='DESCENDING')\
                         .order_by('__name__', direction='ASCENDING')\
                         .limit(limit)
        users_snapshot = query.get(timeout=5)
        
        leaderboard_data = []
        for doc in users_snapshot:
            doc_data = doc.to_dict()
            if doc_data:
                entry = {
                    'id': doc.id,
                    'name': f"{doc_data.get('first_name', '')} {doc_data.get('last_name', '')}".strip(),
                    'credits': doc_data.get('credits', 0)
                }
                leaderboard_data.append(entry)
        
        # Cache only if we got valid data
        if leaderboard_data:
            leaderboard_ref.set({
                'rankings': leaderboard_data,
                'last_updated': int(time.time())  # Store as int
            })
        
        return jsonify({
            "data": leaderboard_data,
            "count": len(leaderboard_data),
            "cached": False
        }), 200

    except Exception as e:
        print(f"Leaderboard Error: {e}")

        # If Firestore query fails, try using old cache as fallback
        try:
            cached_data = leaderboard_ref.get()
            if cached_data.exists:
                return jsonify({
                    "data": cached_data.to_dict().get('rankings', [])[:limit],
                    "count": len(cached_data.to_dict().get('rankings', [])),
                    "cached": True,
                    "fallback": True
                }), 200
        except:
            pass
            
        return jsonify({
            "error": "Leaderboard temporarily unavailable",
            "retry": True
        }), 503