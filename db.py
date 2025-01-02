import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred)

# Global Firestore client
db = firestore.client()

def get_collection_reference(collection_name):
    return db.collection(collection_name)

def get_document_reference(collection_name, document_id):
    return db.collection(collection_name).document(document_id)
