
# routes/login.py
from flask import jsonify, request, session
from models import User, Session
from extensions import db
import datetime
import secrets
from services.generate_jwt import generate_jwt
from services.generate_jwt import generate_refresh_token
from services.validate_jwt import validate_jwt
from services.store_refresh_token import store_refresh_token

def login():
    try:
        data = request.get_json()
        gmail = data.get('email')
        hashed_password = data.get('hashed_password')
        device_info = data.get('device_info')
        # Debug: Print received gmail and password
        print(f"Debug: Received gmail: {gmail}, password: {hashed_password}")

        # Check if gmail and password are provided
        if not gmail or not hashed_password:
            return jsonify({"message": "gmail and password are required"}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=gmail).first()

        if not user or not user.password_hash:
            return jsonify({"message": "User not found"}), 404

        # Verify the password using the salt from the database
        if not user.password_salt:
            return jsonify({"message": "Password salt not found for user"}), 400

        if hashed_password != user.password_hash:
            return jsonify({"message": "Incorrect password"}), 400

        # Check if the user has finished registration (PIN creation)
        if not user.finishedRegistration:
            return jsonify({"message": "User needs to complete PIN creation", "redirect": "/createPin",
                            "info": "It seems that the registration process was incomplete."}), 403
        if user.isFrozen:
            return jsonify({"message": "User account is frozen. Please contact IT support."}), 403

        try:
            # Generate JWT token
            jwt_token = generate_jwt(user.id, device_info)
        except Exception as e:
            print(f"Error generating JWT token: {e}")
            return jsonify({"message": "Error generating JWT token"}), 500

        try:
            refresh_token = generate_refresh_token(user.gmail)
            store_refresh_token(user.gmail, refresh_token, device_info)
        except Exception as e:
            print(f"Error generating or storing refresh token: {e}")
            return jsonify({"message": "Error generating or storing refresh token"}), 500

        # Return the JWT token to the client
        return jsonify({
            "message": "Login successful",
            "user_email": user.gmail,
            "uid": user.id,
            "jwt_token": jwt_token,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "graduation_year": user.graduation_year,
            "pin_hash": user.pin_hash,
            "pin_salt": user.pin_salt
        }), 200

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"message": "An error occurred during login"}), 500