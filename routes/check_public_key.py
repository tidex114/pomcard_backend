from flask import request, jsonify
from models import User

def check_public_key():
    try:
        data = request.get_json()
        email = data.get('email')
        public_key = data.get('public_key')

        if not email or not public_key:
            return jsonify({'error': 'Email and public key are required'}), 400

        # Query the database to find the user with the provided email
        user = User.query.filter_by(gmail=email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if the provided public key matches the user's stored public key
        if user.public_key == public_key:
            return jsonify({'message': 'Public key matches'}), 200
        else:
            return jsonify({'error': 'Public key does not match'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
