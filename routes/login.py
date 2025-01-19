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
        print(f"Debug: Received gmail: {gmail}, password: {hashed_password}, device info: {device_info}")

        if not gmail or not hashed_password:
            return jsonify({"error": "Email and password are required."}), 400

        # Check if user exists in the database
        user = User.query.filter_by(gmail=gmail).first()
        if not user or user.password_hash != hashed_password:
            return jsonify({"error": "Invalid email or password."}), 401

        # Generate JWT tokens
        access_token = generate_jwt(uid=user.id, device_info=device_info)
        refresh_token = generate_refresh_token(uid=user.id, device_info=device_info)

        # Store the refresh token
        store_refresh_token(user.id, refresh_token, device_info)

        db.session.commit()

        # Return the tokens and a success message
        return jsonify({
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "graduation_year": user.graduation_year,
            "user_email": user.gmail,
            "uid": user.id
        }), 200


    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "An error occurred during login. Please try again."}), 500
