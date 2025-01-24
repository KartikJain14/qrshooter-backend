from flask import request, jsonify
from db import get_document_reference
from models.user_model import User

def validate_contact_info(email, phone_number):
    if not email and not phone_number:
        return False, "At least one of email or phone_number is required."
    return True, ""

def add_user():
    try:
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        user_points = int(data.get('user_points', 0))  # Default to 0 points if not provided

        # Validate that at least one of email or phone_number is provided
        is_valid, error_message = validate_contact_info(email, phone_number)
        if not is_valid:
            return {"error": error_message}, 400

        # Create a new User instance
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            credits=user_points  # Pass points directly as integer
        )
        
        # Save user to database
        user.save()

        return {"message": "User added successfully", "user": user.to_dict()}, 201
    except Exception as e:
        return {"error": str(e)}, 400

def update_profile():
    try:
        data = request.json
        unique_id = data.get('unique_id')

        # Retrieve user from database
        user = User.get_by_id(unique_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate that at least one of email or phone_number is provided
        email = data.get('email', user.email)
        phone_number = data.get('phone_number', user.phone_number)
        is_valid, error_message = validate_contact_info(email, phone_number)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Update fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = email
        user.phone_number = phone_number

        # Save updated user
        user.save()

        return jsonify({"message": "User profile updated successfully", "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def delete_profile():
    try:
        data = request.json
        unique_id = data.get('unique_id')
        user = User.get_by_id(unique_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Delete user from database
        user_ref = get_document_reference('users', unique_id)
        user_ref.delete()

        return jsonify({"message": "User profile deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def get_profile(unique_id):
    try:
        user = User.get_by_id(unique_id)
        if user:
            return jsonify({"user": user.to_dict()}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
