from flask import jsonify, render_template, redirect, request
from dotenv import load_dotenv
from db import get_collection_reference
from controllers.admin_controller import add_user
from models.user_model import User
import os

load_dotenv()

db = get_collection_reference('users')

def home():
    user_list = db
    users = []
    for doc in user_list.stream():
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        user_data['name'] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        user_data['credits'] = user_data.get('credits', 0)
        user_data['role'] = user_data.get('role', 'User')
        users.append(user_data)
    return render_template("HomePage.html", users=users)

def add_user_logic(data):
    try:
        first_name= data.get('first_name')
        last_name= data.get('last_name')
        email= data.get('email')
        phone_number= data.get('phone_number')
        user_points= int(data.get('user_points', 0))
        if not email and not phone_number:
            return jsonify({"error": "At least one of email or phone_number is required"}), 400
        
        user = User(
            unique_id=None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            credits=user_points
        )

        user.save()
        return {"message": "User added successfully", "user": user.to_dict()}, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def user_details(user_id):
    try:
        user_ref = db.document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_data['unique_id'] = user_id
            return render_template("UserDetails.html", user=user_data)
        return "User not found", 404
    except Exception as e:
        return str(e), 500

def update_user_points_logic(user_id, points):
    try:
        user_ref = db.document(user_id)
        user_ref.update({'credits': points})
        return redirect(f"{os.getenv('ADMIN_PORTAL')}/user/{user_id}")
    except Exception as e:
        return str(e), 500


def update_user_role_logic(user_id, new_role):
    try:
        db.document(user_id).update({'role': new_role})
        return redirect(f"{os.getenv('ADMIN_PORTAL')}/user/{user_id}")
    except Exception as e:
        return str(e), 500

def delete_user_logic(user_id):
    try:
        db.document(user_id).delete()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return str(e), 500

def get_user_transactions_logic(user_id):
    try:
        # Get user document
        user_ref = db.document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'transactions': []}), 200
            
        user_data = user_doc.to_dict()
        transactions = user_data.get('transaction_history', [])
        
        # Sort transactions by timestamp in descending order
        transactions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"Found {len(transactions)} transactions for user {user_id}")
        return jsonify({'transactions': transactions}), 200
        
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500

def update_user_balance_logic(user_id, balance):
    try:
        user_ref = db.document(user_id)
        user_ref.update({'balance': balance})
        return redirect(f"{os.getenv('ADMIN_PORTAL')}/user/{user_id}")
    except Exception as e:
        return str(e), 500
