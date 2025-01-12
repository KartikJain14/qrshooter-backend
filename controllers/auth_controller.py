from flask import request, jsonify
from google.cloud import firestore
from models.user_model import User
from db import get_collection_reference, get_document_reference
from datetime import datetime, timedelta, timezone
from utils import send_otp, verify_otp
from firebase_admin import auth

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

        verification_id = send_otp(phone_number)
        
        db = get_collection_reference('phone_auth')
        doc_ref = db.document(verification_id)
        doc_ref.set({
            'phone_number': phone_number,
            'verification_id': verification_id,
            'verified': False,
            'attempts': 0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5)
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

        # Verify phone number matches
        if doc_data['phone_number'] != phone_number:
            return jsonify({"error": "Phone number does not match verification record"}), 400

        # Verify code using the verify_otp function
        if not verify_otp(phone_number, verification_id, verification_code):
            return jsonify({"error": "Invalid verification code"}), 400

        # Mark as verified
        doc_ref.update({
            'verified': True,
            'verified_at': firestore.SERVER_TIMESTAMP,
            'verification_code': verification_code  # Store for audit
        })

        # Generate Firebase custom token
        try:
            custom_token = auth.create_custom_token(phone_number)
            token = custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        except Exception as e:
            return jsonify({"error": f"Error generating auth token: {str(e)}"}), 500

        return jsonify({
            "message": "Phone number verified successfully",
            "token": token,
            "phone_number": phone_number
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Verification failed",
            "details": str(e)
        }), 500