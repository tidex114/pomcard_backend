from flask import request, jsonify
from models import db, User
from bcrypt import checkpw

def validate_pin():
    try:
        # Parse request data
        data = request.get_json()
        uid = data.get('uid')
        hashed_pin = data.get('hashed_pin')

        # Check if required fields are present
        if not uid or not hashed_pin:
            return jsonify({'message': 'Missing uid or hashed_pin'}), 400

        # Query the user by ID
        user = User.query.filter_by(id=uid).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Verify the hashed PIN
        if not user.pin_hash:
            return jsonify({'message': 'No PIN is set for this user'}), 400

        if user.pin_hash == hashed_pin:
            return jsonify({'pin_valid': True, 'message': 'PIN verified successfully'}), 200
        else:
            return jsonify({'pin_valid': False, 'message': 'Invalid PIN'}), 403

    except Exception as e:
        print(f"Error during PIN verification: {e}")
        return jsonify({'message': 'Internal server error'}), 500