# routes/login.py
from flask import jsonify, request, session
from models import User, Session
from extensions import db
import datetime
import secrets


def login():
    try:
        data = request.get_json()
        email = data.get('email')
        hashed_password = data.get('hashed_password')

        # Debug: Print received email and password
        print(f"Debug: Received email: {email}, password: {hashed_password}")

        # Check if email and password are provided
        if not email or not hashed_password:
            return jsonify({"message": "Email and password are required"}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=email).first()

        if not user.password_hash:
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
        # Create a session for the user
        session['user_id'] = user.id

        # Generate a session token
        session_token = secrets.token_hex(16)

        # Set session expiration time
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)

        # Create a new session entry in the sessions table
        new_session = Session(
            user_id=user.id,
            session_token=session_token,
            created_at=datetime.datetime.utcnow(),
            expires_at=expires_at
        )
        db.session.add(new_session)
        db.session.commit()

        # Return the session token to the client
        return jsonify({
            "message": "Login successful",
            "session_token": session_token,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "graduation_year": user.graduation_year,
            "barcode": user.barcode,
            "pin_hash": user.pin_hash,
            "pin_salt": user.pin_salt
        }), 200

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"message": "An error occurred during login"}), 500


def validate_session():
    try:
        data = request.get_json()
        session_token = data.get('session_token')

        if not session_token:
            return jsonify({"message": "Session token is required"}), 400

        # Check if session exists and is valid
        session_entry = Session.query.filter_by(session_token=session_token).first()

        if not session_entry or session_entry.expires_at < datetime.datetime.utcnow():
            return jsonify({"message": "Session is invalid or expired"}), 401

        return jsonify({"message": "Session is valid"}), 200

    except Exception as e:
        print(f"Error during session validation: {e}")
