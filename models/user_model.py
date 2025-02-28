from models.role_model import Role
from db import get_collection_reference, get_document_reference
import datetime
import random
import string

class User:
    def __init__(self, first_name: str, last_name: str, unique_id: str = None, email: str = "", phone_number: str = "", is_user: bool = False, is_admin: bool = False, is_sales: bool = False, credits: int = 0, transaction_history: list = None, balance=0, referral_code:str=None, referred_by:list[str]=None):
        self.unique_id = unique_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.role = Role.USER if is_user else (Role.ADMIN if is_admin else (Role.SALES if is_sales else Role.USER))
        self.credits = credits
        self.transaction_history = transaction_history if transaction_history is not None else []
        self.balance = balance
        self.referral_code = referral_code or generate_referral_code()
        self.referred_by = referred_by
        self.referrals = []  

    def to_dict(self):
        return {
            'unique_id': self.unique_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role.value,
            'credits': self.credits,
            'transaction_history': self.transaction_history,
            'balance': self.balance,
            'referral_code': self.referral_code,
            'referred_by': self.referred_by
        }

    def save(self):
        users_ref = get_collection_reference('users')
        
        if self.unique_id:
            # Update an existing document if unique_id is set
            user_ref = get_document_reference('users', self.unique_id)
            user_ref.update(self.to_dict())  # Use `update()` to modify the document
            print(f"Document with ID {self.unique_id} updated.")
        else:
            # If unique_id doesn't exist, add the new user document and get the reference
            update_time, new_user_ref = users_ref.add(self.to_dict())  # Unpack the tuple
            self.unique_id = new_user_ref.id  # Set the unique_id from the auto-generated Firestore ID
            print(f"Document created with ID: {self.unique_id} at {update_time}")

    def update_credits(self, amount: int, transaction_type: str, action_user: str):
        # Ensure that credits don't go below 0 for redemption
        if self.credits + amount < 0:
            raise ValueError("Insufficient credits to redeem")
        
        # Add or subtract the credits
        self.credits += amount

        # Add the transaction entry for the action (either allocated or redeemed)
        transaction_entry = {
            "type": transaction_type,
            "points": amount,
            "timestamp": datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            "balance": self.credits,
            "action_user": action_user
        }
        self.transaction_history.append(transaction_entry)

        # Save the updated user data
        self.save()

    def get_current_credits(self):
        return self.credits

    @classmethod
    def get_by_id(cls, unique_id):
        users_ref = get_collection_reference('users')
        user_ref = users_ref.document(unique_id)
        user_data = user_ref.get()
        if user_data.exists:
            user_dict = user_data.to_dict()
            user = cls(
                unique_id=user_data.id,  # Access the Firestore document ID
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                email=user_dict['email'],
                phone_number=user_dict['phone_number'],
                is_user=user_dict['role'] == Role.USER.value,
                is_admin=user_dict['role'] == Role.ADMIN.value,
                is_sales=user_dict['role'] == Role.SALES.value,
                credits=user_dict['credits'],  # Initialize credits correctly
                transaction_history=user_dict.get('transaction_history', []),
                balance=user_dict.get('balance', 0),
                referral_code=user_dict.get('referral_code', None),
                referred_by=user_dict.get('referred_by', [])
            )
            return user
        return None

    @classmethod
    def get_all(cls):
        users_ref = get_collection_reference('users')
        users_data = users_ref.stream()
        users = []
        for user_data in users_data:
            user_dict = user_data.to_dict()
            user = cls(
                unique_id=user_data.id,  # Get the Firestore document ID
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                email=user_dict['email'],
                phone_number=user_dict['phone_number'],
                is_user=user_dict['role'] == Role.USER.value,
                is_admin=user_dict['role'] == Role.ADMIN.value,
                is_sales=user_dict['role'] == Role.SALES.value,
                credits=user_dict['credits'],  # Initialize credits correctly
                transaction_history=user_dict.get('transaction_history', []),
                balance=user_dict.get('balance', 0),
                referral_code=user_dict.get('referral_code', None),
                referred_by=user_dict.get('referred_by', [])
            )
            users.append(user)
        return users

def generate_referral_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    db = get_collection_reference('users')
    users = db.where('referral_code', '==', code).get()
    if len(users) > 0:
        return generate_referral_code()
    return code