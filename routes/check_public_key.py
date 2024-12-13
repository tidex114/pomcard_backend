from flask import request, jsonify
from models import User

def check_public_key():
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        public_key = data.get('public_key')

        if not first_name or not last_name or not public_key:
            return jsonify({'error': 'First name, last name, and public key are required'}), 400

        # Query the database to find the user with the provided first and last name
        user = User.query.filter_by(first_name=first_name, last_name=last_name).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if the provided public key matches the user's stored public key
        if user.public_key == public_key:
            return jsonify({'message': 'Public key matches'}), 200
        else:
            return jsonify({'error': 'Public key does not match'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500