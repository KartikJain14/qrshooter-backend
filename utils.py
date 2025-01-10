import requests
from app import app

def send_otp(phone_number):
    url = f'https://cpaas.messagecentral.com/verification/v3/send?countryCode=91&customerId={app.config['OTP_CUSTOMER_ID']}&flowType=SMS&mobileNumber={phone_number}'

    payload = {}
    headers = {
        'authToken': app.config['OTP_AUTH_TOKEN']
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('data', {}).get('verificationId')

def verify_otp(phone_number, verification_id, otp):
    url = f'https://cpaas.messagecentral.com/verification/v3/validateOtp?countryCode=91&mobileNumber={phone_number}&verificationId={verification_id}&customerId={app.config["OTP_CUSTOMER_ID"]}&code={otp}'

    payload = {}
    headers = {
        'authToken': app.config['OTP_AUTH_TOKEN']
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('data', {}).get('verificationStatus') == 'VERIFICATION_COMPLETED'