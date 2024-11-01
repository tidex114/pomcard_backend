from flask import request, jsonify
from models import User
from extensions import db

def get_salt():
    try:
        data = request.get_json()
        email = data.get('email')

        # Check if the email is provided
        if not email:
            return jsonify({"message": "Email is required"}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=email).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        # Return the salt to the client
        return jsonify({"password_salt": user.password_salt}), 200

    except Exception as e:
        # Log the exception and return a server error
        print(f"Error during salt retrieval: {e}")
        return jsonify({"message": "An error occurred during salt retrieval"}), 500