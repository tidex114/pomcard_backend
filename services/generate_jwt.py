import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
ISSUER = os.getenv('ISSUER')
AUDIENCE = os.getenv('AUDIENCE')

def generate_jwt(uid, full_name, device_info, expiration_minutes=0.5):
    payload = {
        'sub': str(uid),
        'name': full_name,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes),
        'aud': AUDIENCE,
        'iss': ISSUER,
        'device_info': device_info
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def generate_refresh_token(uid, full_name, device_info, expiration_days=7):
    payload = {
        'sub': str(uid),
        'name': full_name,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        'aud': AUDIENCE,
        'iss': ISSUER,
        'device_info': device_info
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token