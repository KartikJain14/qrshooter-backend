from flask import request, jsonify
from google.cloud import firestore
from models.user_model import User
from db import get_collection_reference, get_document_reference
from datetime import datetime, timedelta, timezone
from utils import send_otp, verify_otp

def check_phone_exists(phone_number):
    db = firestore.Client()
    users = db.collection('users').where('phone_number', '==', phone_number).get()
    return len(list(users)) > 0

def send_verification_code():
    try:
        # Phone number should be 10 digits, no country code required
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        # Check if phone number already exists in db
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
        verification_id = request.json.get('verification_id')
        verification_code = request.json.get('verification_code')
        phone_number = request.json.get('phone_number')
        first_name = request.json.get('first_name', '')
        last_name = request.json.get('last_name', '')

        if not all([verification_id, verification_code, phone_number]):
            return jsonify({"error": "Missing required fields"}), 400
        
        db = get_collection_reference('phone_auth')
        doc_ref = db.document(verification_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Invalid verification ID"}), 400

        doc_data = doc.to_dict()
        
        if datetime.now(timezone.utc) > doc_data['expires_at']:
            return jsonify({"error": "Verification code expired"}), 400

        if doc_data['attempts'] >= 5:
            return jsonify({"error": "Too many attempts"}), 400

        doc_ref.update({'attempts': doc_data['attempts'] + 1})

        if verify_otp(phone_number, verification_id, verification_code):
            return jsonify({"message": "OTP verified"}), 200

        return jsonify({"error": "Invalid verification code"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400