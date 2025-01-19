from flask import request, jsonify
from models import RefreshToken
from extensions import db

def logout():
    try:
        # Parse request data
        data = request.get_json()
        uid = data.get('uid')

        if not uid:
            return jsonify({'message': 'User ID (uid) is required'}), 400

        # Find all refresh tokens associated with the given uid
        tokens = RefreshToken.query.filter_by(user_id=uid).all()

        if not tokens:
            return jsonify({'message': 'No refresh tokens found for the given user'}), 404

        # Remove all refresh tokens for this user
        for token in tokens:
            db.session.delete(token)
        db.session.commit()

        return jsonify({'message': 'Successfully logged out'}), 200

    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({'message': 'Internal server error'}), 500
