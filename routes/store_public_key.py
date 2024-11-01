from flask import request, jsonify
from extensions import db
from models import User
import json

def store_public_key():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        email = data.get('email')
        public_key = data.get('public_key')

        if not email or not public_key:
            print("Missing email or public key")
            return jsonify({'message': 'Email and public key are required'}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=email).first()
        print(f"User lookup result: {user}")

        if user is None:
            print("User not found")
            return jsonify({'message': 'User not found'}), 404

        # Store the public key as a plain string
        user.public_key = public_key
        db.session.commit()
        print("Public key stored successfully in the database")

        return jsonify({'message': 'Public key stored successfully'}), 200

    except Exception as e:
        print(f"Error during storing public key: {e}")
        return jsonify({'message': 'An error occurred while storing the public key'}), 500
