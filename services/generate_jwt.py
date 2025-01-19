import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
ISSUER = os.getenv('ISSUER')

def generate_jwt(uid, device_info, expiration_minutes=15):
    payload = {
        'sub': uid,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes),
        'aud': device_info,
        'iss': ISSUER
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def generate_refresh_token(uid, device_info, expiration_days=7):
    payload = {
        'sub': uid,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiration_days),
        'aud': device_info,
        'iss': ISSUER
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token