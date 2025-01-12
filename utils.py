import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_otp(phone_number):
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {"authorization":os.getenv('OTP_AUTH_TOKEN'),"variables_values":"5598","route":"otp","numbers":phone_number}

        headers = {
                'cache-control': "no-cache"
                }

        response = requests.request("GET", url, headers=headers, params=querystring)
        print(response.text)
        return response.json().get('data', {}).get('verificationId')
    except Exception as e:
        raise e



def verify_otp(phone_number, verification_id, otp):
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = f"variables_values={otp}&route=otp&numbers={phone_number}"
        headers = {
            'authorization': os.getenv('OTP_AUTH_TOKEN'),
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        result = response.json()
        return result.get('data', {}).get('verificationStatus') == 'VERIFICATION_COMPLETED'
    except Exception as e:
        return False