from flask import request, jsonify
from models import db, User

def get_pin_salt():
    try:
        # Parse the request data
        data = request.get_json()
        uid = data.get('uid')

        # Validate the input
        if not uid:
            return jsonify({'message': 'UID is required'}), 400

        # Fetch the user from the database
        user = User.query.filter_by(id=uid).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Return the pin_salt
        if user.pin_salt:
            return jsonify({'pin_salt': user.pin_salt}), 200
        else:
            return jsonify({'message': 'PIN salt not found for the user'}), 404

    except Exception as e:
        print(f"Error fetching PIN salt: {e}")
        return jsonify({'message': 'An internal server error occurred'}), 500