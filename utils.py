import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_otp(phone_number):
    try:
        url = f'https://cpaas.messagecentral.com/verification/v3/send?countryCode=91&customerId={os.getenv("OTP_CUSTOMER_ID")}&flowType=SMS&mobileNumber={phone_number}'
        
        headers = {
            'authToken': os.getenv('OTP_AUTH_TOKEN')
        }

        response = requests.post(url, headers=headers)
        return response.json().get('data', {}).get('verificationId')
    except Exception as e:
        raise e

def verify_otp(phone_number, verification_id, otp):
    try:
        url = f'https://cpaas.messagecentral.com/verification/v3/validateOtp?countryCode=91&mobileNumber={phone_number}&verificationId={verification_id}&customerId={os.getenv("OTP_CUSTOMER_ID")}&code={otp}'
        
        headers = {
            'authToken': os.getenv('OTP_AUTH_TOKEN')
        }

        response = requests.post(url, headers=headers)
        result = response.json()
        return result.get('data', {}).get('verificationStatus') == 'VERIFICATION_COMPLETED'
    except Exception as e:
        return False