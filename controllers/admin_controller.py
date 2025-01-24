from firebase_admin import auth, firestore
from models.role_model import Role
from models.user_model import User
from db import get_document_reference
import base64
import os
from flask import jsonify

def auth_middleware(token):
    if not token:
        return jsonify({"error": "Unauthorized: Token key not provided"}), 401

    token = base64.b64decode(token).decode('utf-8')
    
    if token != os.getenv('ADMIN_PASSWORD'):
        return jsonify({"error": "Unauthorized: Invalid Credentials"}), 401

def get_all_users():
    try:
        users = auth.list_users().users
        user_list = []
        for firebase_user in users:
            user_id = firebase_user.uid
            user_ref = get_document_reference('users', user_id)
            user_data = user_ref.get()
            if user_data.exists:
                user_dict = user_data.to_dict()
                user_list.append({
                    "unique_id": user_data.id,
                    "name": user_dict.get("name"),
                    "credits": user_dict.get("credits"),
                })
        return {"users": user_list}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def update_user_points(user_id, points):
    try:
        user_ref = get_document_reference('users', user_id)
        user_ref.update({"credits": firestore.Increment(points)})
        return {"message": "User points updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def add_user(user_id, user_name, user_points=0):
    try:
        user_ref = get_document_reference('users', user_id)
        user_ref.set({
            "name": user_name,
            "credits": user_points
        })
        return {"message": "User added successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 400

def remove_user(user_id):
    try:
        user_ref = get_document_reference('users', user_id)
        user_ref.delete()
        return {"message": "User removed successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def change_user_role(admin_id,target_user_id, new_role):
    try:
        admin_user=User.get_by_id(admin_id)
        if not admin_user or admin_user.role != Role.ADMIN:
            return {"error": "Unauthorized"}, 403
        
        target_user = User.get_by_id(target_user_id)
        if not target_user:
            return {"error": "User not found"}, 404
        
        try:
            new_role_enum = Role(new_role.upper())
        except KeyError:
            return{"error": "Invalid role"}, 400
        
        user_ref = get_document_reference('users', target_user_id)
        user_ref.update({"role": new_role_enum.value})
        return {
            "message": f"User role updated to {new_role} successfully",
            "user": {
                "id": target_user_id,
                "role": new_role_enum.value
            }
        },200
    except Exception as e:
        return {"error": str(e)}, 400
    
