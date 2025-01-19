# services/store_refresh_token.py
from models import RefreshToken
from extensions import db
import datetime
import bcrypt


def store_refresh_token(uid, refresh_token, device_info):
    """Store the hashed refresh token in the database."""
    # Hash the refresh token
    hashed_token = bcrypt.hashpw(refresh_token.encode(), bcrypt.gensalt()).decode()

    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    new_refresh_token = RefreshToken(
        refresh_token=refresh_token,
        created_at=datetime.datetime.utcnow(),
        expires_at=expires_at,
        device_model=device_info,
        user_id=uid  # Ensure this is set correctly and not None
    )
    db.session.add(new_refresh_token)
    db.session.commit()

    return refresh_token
