# middleware.py
from flask import request, jsonify
from services.validate_jwt import validate_jwt

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        token = token.split(" ")[1]  # Assuming the token is in the format "Bearer <token>"
        validation_response = validate_jwt(token)
        if 'error' in validation_response:
            return jsonify({'message': validation_response['error']}), 401

        return f(*args, **kwargs)
    return decorated