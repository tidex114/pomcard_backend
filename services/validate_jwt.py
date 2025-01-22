import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
AUDIENCE = os.getenv('AUDIENCE')
ISSUER = os.getenv('ISSUER')

def validate_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], audience=AUDIENCE, issuer=ISSUER)
        return payload
    except ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except InvalidTokenError:
        return {'error': 'Invalid token'}