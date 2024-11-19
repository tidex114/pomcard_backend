from flask import request, jsonify
from extensions import db
from models import User, Session
from datetime import datetime

def validate_session():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Query the database to find the user with the provided email
        user = User.query.filter_by(gmail=email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Query the database to find the session(s) associated with the user
        sessions = Session.query.filter_by(user_id=user.id).all()

        if not sessions:
            return jsonify({'error': 'No sessions found for this user'}), 404

        valid_session_exists = False

        for session in sessions:
            # Check if the session has expired
            if session.expires_at < datetime.utcnow():
                # Session is expired, remove it from the database
                db.session.delete(session)
                db.session.commit()
            else:
                valid_session_exists = True

        if valid_session_exists:
            return jsonify({'code': 2}), 200
        else:
            return jsonify({'error': 'All sessions expired and have been removed'}), 404

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
