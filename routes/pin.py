# routes/pin.py
from flask import jsonify, request
from models import User
from extensions import db
import secrets

def save_pin():
    try:
        data = request.get_json()
        email = data.get('email')
        pin_hash = data.get('pin_hash')
        pin_salt = data.get('pin_salt')
        password_hash = data.get('password_hash')
        password_salt = data.get('password_salt')
        print(data)

        # Check if email, pin_hash, pin_salt, password_hash, and password_salt are provided
        if not email or not pin_hash or not pin_salt or not password_hash or not password_salt:
            return jsonify({"message": "Email, PIN hash, PIN salt, password hash, and password salt are required"}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=email).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        session_token = secrets.token_hex(16)
        print(f"Debug: Generated session token: {session_token}")

        # Store the hashed PIN, salt, password hash, and password salt in the user record
        user.pin_hash = pin_hash
        user.pin_salt = pin_salt
        user.password_hash = password_hash
        user.password_salt = password_salt
        user.finishedRegistration = True
        db.session.commit()

        return jsonify({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "graduation_year": user.graduation_year,
            "message": "Login successful",
            "session_token": session_token,
            "pin_hash": user.pin_hash,
            "pin_salt": user.pin_salt
        }), 200
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"message": "An error occurred during login"}), 500