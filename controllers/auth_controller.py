from flask import request, jsonify
from firebase_admin import auth
from google.cloud import firestore
from models.user_model import User
import uuid
import random
from datetime import datetime, timedelta, timezone

def format_phone_number(phone):
    phone = ''.join(filter(str.isdigit, phone))
    if not phone.startswith('91'):
        phone = '91' + phone
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

def check_phone_exists(phone_number):
    db = firestore.Client()
    users = db.collection('users').where('phone_number', '==', phone_number).get()
    return len(list(users)) > 0

def send_verification_code():
    try:
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        phone_number = format_phone_number(phone_number)
        # Check if phone number already exists in db
        if check_phone_exists(phone_number):
            return jsonify({"error": "Phone number already registered"}), 400

        verification_id = str(uuid.uuid4())
        otp = str(random.randint(100000, 999999))
        
        db = firestore.Client()
        doc_ref = db.collection('phone_auth').document(verification_id)
        doc_ref.set({
            'phone_number': phone_number,
            'verification_id': verification_id,
            'otp': otp,
            'verified': False,
            'attempts': 0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5)
        })

        return jsonify({
            "message": "Verification code sent",
            "verification_id": verification_id,
            "otp_code": otp
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

        phone_number = format_phone_number(phone_number)
        
        db = firestore.Client()
        doc_ref = db.collection('phone_auth').document(verification_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Invalid verification ID"}), 400

        doc_data = doc.to_dict()
        
        if datetime.now(timezone.utc) > doc_data['expires_at']:
            return jsonify({"error": "Verification code expired"}), 400

        if doc_data['attempts'] >= 3:
            return jsonify({"error": "Too many attempts"}), 400

        doc_ref.update({'attempts': doc_data['attempts'] + 1})

        if verification_code != doc_data['otp']:
            return jsonify({"error": "Invalid verification code"}), 400

        # Create new user if verification successful
        user = User(
            unique_id=None,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            is_user=True,
            credits=0
        )
        user.save()

        custom_token = auth.create_custom_token(phone_number)

        return jsonify({
            "message": "Phone number verified",
            "token": custom_token.decode('utf-8'),
            "user": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def google_sign_in():
    try:
        id_token = request.json.get('id_token')
        if not id_token:
            return jsonify({"error": "ID token is required"}), 400
            
        decoded_token = auth.verify_id_token(id_token)
        return jsonify({"decoded_token": decoded_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400