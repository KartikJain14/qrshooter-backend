from flask import request, jsonify
from firebase_admin import auth
from google.cloud import firestore
import uuid

def send_verification_code():
    try:
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        # Generate verification ID
        verification_id = str(uuid.uuid4())
        
        # Store verification attempt
        db = firestore.Client()
        doc_ref = db.collection('phone_auth').document(verification_id)
        doc_ref.set({
            'phone_number': phone_number,
            'verification_id': verification_id,
            'verified': False,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "message": "Verification code sent",
            "verification_id": verification_id,
            "test_code": "123456"  # For testing only
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def verify_code():
    try:
        verification_id = request.json.get('verification_id')
        verification_code = request.json.get('verification_code')
        phone_number = request.json.get('phone_number')

        if not all([verification_id, verification_code, phone_number]):
            return jsonify({"error": "Missing required fields"}), 400

        # Verify code
        if verification_code != "123456":
            return jsonify({"error": "Invalid verification code"}), 400

        # Get verification attempt
        db = firestore.Client()
        doc_ref = db.collection('phone_auth').document(verification_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Invalid verification ID"}), 400

        doc_data = doc.to_dict()
        if doc_data['phone_number'] != phone_number:
            return jsonify({"error": "Phone number mismatch"}), 400

        # Mark as verified
        doc_ref.update({
            'verified': True,
            'verified_at': firestore.SERVER_TIMESTAMP
        })

        # Generate auth token
        custom_token = auth.create_custom_token(phone_number)

        return jsonify({
            "message": "Phone number verified",
            "token": custom_token.decode('utf-8'),
            "phone_number": phone_number
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