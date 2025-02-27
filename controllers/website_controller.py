from flask import jsonify, render_template, redirect, request
from dotenv import load_dotenv
from db import get_collection_reference
from controllers.admin_controller import add_user
from models.user_model import User
import os

load_dotenv()

db = get_collection_reference('users')

def home():
    sort_by = "default"
    if request.method == "POST":
        sort_by = request.form.get("sortbtn")
        # Redirect with sort parameter
        return redirect(f"{os.getenv('ADMIN_PORTAL')}?sort={sort_by}")
    
    # Get sort from query parameter if GET request
    sort_by = request.args.get('sort', 'default')
    
    user_list = db
    users = []
    for doc in user_list.stream():
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        user_data['name'] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        user_data['credits'] = user_data.get('credits', 0)
        user_data['role'] = user_data.get('role', 'User')
        users.append(user_data)

    if sort_by != "default":
        users = [user for user in users if user["role"] == sort_by]
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

def search_users():
    query = request.args.get('query', '')
    print(f"Search query received: '{query}'")

    if not query or query.strip() == '':
        print("Empty query, returning all users")
        return home()

    query = query.lower().strip()
    users = []

    try:
        print(f"Processing search for: '{query}'")
        # Get all users first
        all_docs = list(db.stream())
        print(f"Total users in database: {len(all_docs)}")

        for doc in all_docs:
            user_data = doc.to_dict()
            user_id = doc.id

            # Get the searchable fields
            first_name = user_data.get('first_name', '').lower() if user_data.get('first_name') else ''
            last_name = user_data.get('last_name', '').lower() if user_data.get('last_name') else ''
            full_name = f"{first_name} {last_name}".strip()
            email = user_data.get('email', '').lower() if user_data.get('email') else ''
            phone = user_data.get('phone_number', '').lower() if user_data.get('phone_number') else ''

            print(f"Checking user - ID: {user_id}, Name: '{full_name}', Email: '{email}', Phone: '{phone}'")

            # Use exact substring matching
            found_match = False
            if query in full_name:
                print(f"Match found in name: '{full_name}'")
                found_match = True
            elif query in email:
                print(f"Match found in email: '{email}'")
                found_match = True  
            elif query in phone:
                print(f"Match found in phone: '{phone}'")
                found_match = True
            elif query in user_id.lower():
                print(f"Match found in ID: '{user_id}'")
                found_match = True

            if found_match:
                # Format for display
                user_data['id'] = user_id
                user_data['name'] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                user_data['credits'] = user_data.get('credits', 0)
                user_data['role'] = user_data.get('role', 'User')
                users.append(user_data)

        print(f"Search results: {len(users)} users found")
        return render_template("HomePage.html", users=users, query=query)
    except Exception as e:
        print(f"Search error: {str(e)}")
        return render_template("HomePage.html", users=[], query=query, error=str(e))