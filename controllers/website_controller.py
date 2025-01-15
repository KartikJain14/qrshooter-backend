from flask import jsonify, render_template, redirect, request
from dotenv import load_dotenv
from db import get_collection_reference
from controllers.admin_controller import add_user
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
        user_data = {
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "email": data.get('email'),
            "phone_number": data.get('phone_number'),
            "credits": int(data.get('user_points', 0))
        }
        response = add_user(user_data)
        return jsonify(response), 200
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
        db.document(user_id).update({'credits': points})
        return redirect(f"/user/{user_id}")
    except Exception as e:
        return str(e), 500

def update_user_role_logic(user_id, new_role):
    try:
        db.document(user_id).update({'role': new_role})
        return redirect(f"/user/{user_id}")
    except Exception as e:
        return str(e), 500

def delete_user_logic(user_id):
    try:
        db.document(user_id).delete()
        return redirect("/home")
    except Exception as e:
        return str(e), 500

def get_user_transactions_logic(user_id):
    try:
        transactions_ref = get_collection_reference('transactions')
        transactions = transactions_ref.where('user_id', '==', user_id).stream()
        
        transaction_list = []
        for transaction in transactions:
            trans_data = transaction.to_dict()
            trans_data['id'] = transaction.id
            trans_data['timestamp'] = trans_data.get('timestamp', '').strftime('%Y-%m-%d %H:%M:%S')
            transaction_list.append(trans_data)
            
        transaction_list.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(transaction_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
