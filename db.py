import os
from dotenv import load_dotenv, dotenv_values
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    # Firebase credentials loaded from environment variables
    firebase_credentials = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),  # Ensure correct private key format
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
    }

    # Initialize Firebase using the environment variables directly
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Global Firestore client
db = firestore.client()

def get_collection_reference(collection_name):
    return db.collection(collection_name)

def get_document_reference(collection_name, document_id):
    return db.collection(collection_name).document(document_id)
