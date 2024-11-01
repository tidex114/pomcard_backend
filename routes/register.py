from flask import jsonify, request, session
from models import RegisteringUser, User
from services import email_verification
from extensions import db
import random
import bcrypt
import datetime

def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if the email is provided and valid
        if not email or not email.endswith('@pomfret.org'):
            return jsonify({"message": "Invalid email format"}), 400

        # Check if password is provided and matches security requirements
        if not password or len(password) < 8:
            return jsonify({"message": "Password must be at least 8 characters"}), 400

        # Check if a session is already active for registration
        if 'email' in session:
            if session['email'] != email:
                return jsonify({"message": "You're already registering with another email."}), 400

        # Check if the user is already registered
        existing_user = User.query.filter_by(gmail=email).first()
        if existing_user and existing_user.password_hash:
            return jsonify({"message": "User is already registered with this email"}), 400

        # Store the email in the session if not already locked
        session['email'] = email

        # Generate a 6-digit verification code
        generated_code = random.randint(100000, 999999)

        # Hash the password securely using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Remove expired codes (older than 10 minutes)
        expiration_time = datetime.datetime.now() - datetime.timedelta(minutes=10)
        RegisteringUser.query.filter(RegisteringUser.code_creation_time < expiration_time).delete()

        # Check if the user is already in the process of registering
        user = RegisteringUser.query.filter_by(email=email).first()

        if user:
            # Update the existing user's code, hashed password, and reset the timer
            user.generated_code = generated_code
            user.hashed_password = hashed_password
            user.code_creation_time = datetime.datetime.now()
            user.is_active = True
        else:
            # Create a new registering user with the hashed password
            user = RegisteringUser(
                email=email,
                generated_code=generated_code,
                hashed_password=hashed_password,
                is_active=True,
                code_creation_time=datetime.datetime.now()
            )
            db.session.add(user)

        # Commit the changes to the database
        db.session.commit()

        # Send the verification code via email
        email_verification.send_verification_email(email, generated_code)

        # DEBUG line to print unhashed code for development purposes
        print(f"Verification code for {email}: {generated_code}")

        return jsonify({"message": "Verification code sent to email"}), 200

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"message": "An error occurred during registration"}), 500

def reset_registration():
    session.pop('email', None)
    return jsonify({"message": "Registration reset. You can now register with a new email."}), 200
