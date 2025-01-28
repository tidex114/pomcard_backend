# services/store_refresh_token.py
import jwt

from models import RefreshToken
from extensions import db
import datetime
import bcrypt
import os
import dotenv

def store_refresh_token(uid, refresh_token, device_info):
    """Store the hashed refresh token in the database."""
    # Hash the refresh token
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    ISSUER = os.getenv('ISSUER')
    AUDIENCE = os.getenv('AUDIENCE')
    salt = bcrypt.gensalt()
    hashed_token = bcrypt.hashpw(refresh_token.encode(), salt).decode()
    decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"], audience=AUDIENCE, issuer=ISSUER)
    expires_at = datetime.datetime.utcfromtimestamp(decoded_token["exp"])
    print("expires_at", expires_at)
    new_refresh_token = RefreshToken(
        refresh_token=hashed_token,
        created_at=datetime.datetime.utcnow(),
        expires_at=expires_at,
        device_model=device_info,
        user_id=uid,
        token_salt=salt.decode('utf-8'),
    )
    print(expires_at)
    db.session.add(new_refresh_token)
    db.session.commit()

    return refresh_token
