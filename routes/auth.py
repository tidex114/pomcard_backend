import bcrypt
from flask import request, jsonify
from models import User, RefreshToken
from extensions import db
from services.generate_jwt import generate_jwt, generate_refresh_token
from services.validate_jwt import validate_jwt
from bcrypt import checkpw
import datetime

def refresh_token():
    try:
        data = request.get_json()
        incoming_refresh_token = data.get('refresh_token')

        if not incoming_refresh_token:
            return jsonify({'message': 'Refresh token is required'}), 400

        # Fetch the stored hashed refresh token from the database
        stored_token_entry = RefreshToken.query.filter_by(refresh_token=incoming_refresh_token).first()

        if not stored_token_entry:
            return jsonify({'message': 'Invalid refresh token'}), 401

        # Validate the incoming refresh token with the stored hashed token
        if not checkpw(incoming_refresh_token.encode('utf-8'), stored_token_entry.refresh_token.encode('utf-8')):
            return jsonify({'message': 'Invalid refresh token'}), 401

        # Fetch the user based on the refresh token entry
        user = User.query.get(stored_token_entry.user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Invalidate the old refresh token
        db.session.delete(stored_token_entry)
        db.session.commit()

        # Generate new tokens
        new_access_token = generate_jwt(user.id)
        new_refresh_token = generate_refresh_token(user.id)

        # Hash the new refresh token before storing it
        hashed_new_refresh_token = bcrypt.hashpw(new_refresh_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Store the new hashed refresh token
        new_refresh_token_entry = RefreshToken(
            user_id=user.id,
            refresh_token=hashed_new_refresh_token,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )
        db.session.add(new_refresh_token_entry)
        db.session.commit()

        return jsonify({
            'access_token': new_access_token,
            'refresh_token': new_refresh_token  # Send plain token back to the user
        }), 200

    except Exception as e:
        print(f"Error during token refresh: {e}")
        return jsonify({'message': 'Internal server error'}), 500
