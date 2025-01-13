from flask import request, jsonify
from google.cloud import firestore
from controllers.user_controller import add_user
from models.user_model import User
from db import get_collection_reference, get_document_reference
from datetime import datetime, timedelta, timezone
from utils import send_otp
from firebase_admin import auth
import base64

def check_phone_exists(phone_number):
    db = get_collection_reference('users')
    users = db.where('phone_number', '==', phone_number).get()
    return len(list(users)) > 0

def send_verification_code():
    try:
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        if check_phone_exists(phone_number):
            return jsonify({"error": "Phone number already registered"}), 400

        verification_id, otp = send_otp(phone_number)
        
        db = get_collection_reference('phone_auth')
        doc_ref = db.document(verification_id)
        doc_ref.set({
            'phone_number': phone_number,
            'verification_id': verification_id,
            'verified': False,
            'attempts': 0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5),
            'otp': otp
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
        if not doc.exists():
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
        if doc_data['otp'] != verification_code:
            return jsonify({"error": "Invalid verification code"}), 400

        token = base64.b64encode(verification_code)

        # Mark as verified
        doc_ref.update({
            'verified': True,
            'verified_at': firestore.SERVER_TIMESTAMP,
            token: token
        })

        return jsonify({
            "message": "Verification successful",
            "token": token
        }), 200

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
        doc_ref = db.document(base64.b64decode(token))
        user = doc_ref.get()
        if not user:
            return jsonify({"error": "User not found"}), 404
        else:
            return add_user(request)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400