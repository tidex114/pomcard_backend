from flask import jsonify, request
from models import RegisteringUser, User
from extensions import db
import datetime
import random
from services import email_verification

def verify_code():
    try:
        data = request.get_json()
        email = data.get('email')
        input_code = data.get('code')

        # Check if email and code are provided
        if not email or not input_code:
            return jsonify({"message": "Email and code are required"}), 400

        # Look up the registering user in the database
        registering_user = RegisteringUser.query.filter_by(email=email).first()

        if not registering_user:
            return jsonify({"message": "User not found in registration attempts"}), 404

        # Check if the user's code matches the input code
        if registering_user.generated_code == input_code:
            # Check if the code has expired
            expiration_time = registering_user.code_creation_time + datetime.timedelta(minutes=10)
            if datetime.datetime.now() > expiration_time:
                return jsonify({"message": "Code expired"}), 400

            # Code is valid and not expired. Now check if the user's email exists in the users table.
            existing_user = User.query.filter_by(gmail=email).first()
            if not existing_user:
                return jsonify({"message": "Your email is not authorized to create an account. Please contact the IT office."}), 403

            # Transfer hashed password from the RegisteringUser to User table

            db.session.commit()

            # Optionally, delete the registration attempt after successful verification
            db.session.delete(registering_user)
            db.session.commit()

            return jsonify({"message": "Code verified successfully. User authorized."}), 200
        else:
            return jsonify({"message": "Invalid code"}), 400

    except Exception as e:
        print(f"Error during code verification: {e}")
        return jsonify({"message": "An error occurred during verification"}), 500

def resend_code():
    try:
        data = request.get_json()
        email = data.get('email')

        # Check if email is provided
        if not email:
            return jsonify({"message": "Email is required"}), 400

        # Look up the registering user in the database
        registering_user = RegisteringUser.query.filter_by(email=email).first()

        if not registering_user:
            return jsonify({"message": "User not found in registration attempts"}), 404

        # Generate a new 6-digit verification code
        generated_code = random.randint(100000, 999999)
        registering_user.generated_code = generated_code
        registering_user.code_creation_time = datetime.datetime.now()
        db.session.commit()

        # Send the verification code via email
        email_verification.send_verification_email(email, generated_code)

        # DEBUG line to print unhashed code for development purposes
        print(f"Resent verification code for {email}: {generated_code}")

        return jsonify({"message": "Verification code resent to email"}), 200

    except Exception as e:
        print(f"Error during resend code: {e}")
        return jsonify({"message": "An error occurred during resend code"}), 500
