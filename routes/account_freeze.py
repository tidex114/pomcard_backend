# routes/account_freeze.py
from flask import request, jsonify
from models import User
from extensions import db

def account_freeze():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        # Look up the user in the database
        user = User.query.filter_by(gmail=email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Set the user's account as frozen
        user.isFrozen = True
        db.session.commit()

        return jsonify({'message': 'User account has been frozen successfully'}), 200
    except Exception as e:
        print(f"Error during account freeze: {e}")
        return jsonify({'message': 'An error occurred during account freeze'}), 500