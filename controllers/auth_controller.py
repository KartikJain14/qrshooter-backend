from flask import request, jsonify
from google.cloud import firestore
from models.user_model import User
from db import get_collection_reference
from datetime import datetime, timedelta, timezone
from utils import send_otp
import base64

def send_verification_code():
    try:
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        verification_id, otp = send_otp(phone_number)
        
        db = get_collection_reference('phone_auth')
        doc_ref = db.document(verification_id)
        doc_ref.set({
            'phone_number': phone_number,
            'verification_id': verification_id,
            'verified': False,
            'attempts': 0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=15),
            'otp': f'{otp}'
        })

        return jsonify({
            "message": f"Verification code sent to {phone_number}",
            "verification_id": verification_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def verify_code():
    try:
        # Get request data
        data = request.get_json()
        verification_id = data.get('verification_id')
        verification_code = data.get('verification_code')
        phone_number = data.get('phone_number')

        # Validate required fields
        if not all([verification_id, verification_code, phone_number]):
            return jsonify({
                "error": "Missing required fields",
                "required": ["verification_id", "verification_code", "phone_number"]
            }), 400

        # Get verification attempt from Firestore
        db = get_collection_reference('phone_auth')
        doc_ref = db.document(verification_id)
        doc = doc_ref.get()

        # Check if document exists
        if doc.exists == False:
            return jsonify({"error": "Invalid verification ID"}), 404

        # Get document data
        doc_data = doc.to_dict()


        # Check if already verified
        if doc_data.get('verified'):
            return jsonify({"error": "Code already verified"}), 400

        # Check if the code has expired 
        if doc_data.get('expires_at') < datetime.now(timezone.utc):
            return jsonify({"error": "Verification code has expired"}), 400
        
        # Verify phone number matches
        if doc_data['phone_number'] != phone_number:
            return jsonify({"error": "Phone number does not match verification record"}), 400

        # Verify code using the verify_otp function
        print(type(doc_data['otp']), type((verification_code)))
        print(doc_data['otp'], (verification_code))
        if doc_data['otp'] != verification_code:
            return jsonify({"error": "Invalid verification code"}), 400

        token = base64.b64encode((phone_number+"::"+verification_id).encode('utf-8')).decode('utf-8')

        # Mark as verified
        doc_ref.update({
            'verified': True,
            'verified_at': firestore.SERVER_TIMESTAMP,
            token: token
        })

        # return jsonify({
        #     "message": "Verification successful",
        #     "token": token
        # }), 200

        db = get_collection_reference('users')
        users = db.where(field_path='phone_number', op_string='==', value=phone_number).get()

        if len(users) > 0:
            user_data = users[0].to_dict()
            user_data['id'] = users[0].id
            return jsonify({
                "message": "User found",
                "user": user_data
            }), 200

        return jsonify({
            "message": "User not found",
            "token": token
        }), 201
    
    except Exception as e:
        return jsonify({
            "error": "Verification failed",
            "details": str(e)
        }), 500
    
def create_user_by_token():
    try:
        data = request.json
        token = data.get('token')
        db = get_collection_reference('phone_auth')
        token = base64.b64decode(token).decode('utf-8')
        phone_number, verification_id = token.split("::")
        doc_ref = db.document(verification_id)
        user = doc_ref.get()

        if not user:
            return jsonify({"error": "Token invalid"}), 404
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        user_points = int(data.get('user_points', 0)) 

        user = User(
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

def search_user_by_email():
    try:
        # Get the email from the POST request
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Query Firestore to check if the email exists
        db = get_collection_reference('users')  # 'users' is the Firestore collection name
        users = db.where(field_path='email', op_string='==', value=email).get()

        # Check if a user with this email exists
        if len(users) > 0:
            # Extract user details
            user_data = users[0].to_dict()  # Get the first matching document's data
            user_data['unique_id'] = users[0].id  # Add the Firestore document ID if needed
            return jsonify({
                "message": "Email already in use",
                "user_exists": True,
                "user": user_data
            }), 200

        # If no user is found
        return jsonify({"message": "Email is available", "user_exists": False}), 200

    except Exception as e:
        return jsonify({"error": "Error searching email", "details": str(e)}), 500

def search_user_by_phone():
    try:
        data = request.get_json()
        phone = data.get('phone')

        if not phone:
            return jsonify({"error": "Phone is required"}), 400

        db = get_collection_reference('users')
        users = db.where(field_path='phone_number', op_string='==', value=phone).get()

        if len(users) > 0:
            user_data = users[0].to_dict()
            user_data['unique_id'] = users[0].id
            return jsonify({
                "message": "Phone already in use",
                "user_exists": True,
                "user": user_data
            }), 200

        # If no user is found
        return jsonify({"message": "Phone is available", "user_exists": False}), 200

    except Exception as e:
        return jsonify({"error": "Error searching phone", "details": str(e)}), 500