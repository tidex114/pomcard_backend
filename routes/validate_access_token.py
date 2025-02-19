import jwt
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import request, jsonify

# Load environment variables
load_dotenv()


def validate_access_token(access_token, uid, full_name):
    try:
        # Retrieve secret and issuer from environment
        secret_key = os.getenv('APP_SECRET_KEY')
        issuer_env = os.getenv('ISSUER')
        audience_env = os.getenv('AUDIENCE')

        if not secret_key or not issuer_env:
            print("Missing environment variables for secret key or issuer")
            return 1  # Reason 1: Missing environment variables

        print("Expected audience from environment:", audience_env)
        print("Expected issuer from environment:", issuer_env)

        # Decode and verify the JWT
        print(access_token)
        payload = jwt.decode(
            access_token,
            secret_key,
            algorithms=["HS256"],
            audience=audience_env,
            options={"require": ["exp", "sub", "name", "aud"]}  # Ensure required claims are present
        )

        # Verify claims
        # `exp` is already checked by jwt.decode if auto-handled

        # Check `sub` (user ID) and convert to string
        if str(payload.get("sub")) != str(uid):
            print("Invalid subject (user ID)")
            return 2  # Reason 2: Invalid subject (user ID)

        # Check `name`
        if payload.get("name") != full_name:
            print("Invalid full name")
            return 3  # Reason 3: Invalid full name

        # Check `iss` (issuer)
        issuer = payload.get("iss")
        if issuer and issuer != issuer_env:
            print("Invalid issuer")
            return 4  # Reason 4: Invalid issuer

        # Token is valid
        print("Access token is valid")
        return 0  # Reason 0: Token is valid

    except jwt.ExpiredSignatureError:
        print("Access token has expired")
        return 5  # Reason 5: Access token has expired
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return 6  # Reason 6: Invalid token
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 7  # Reason 7: An unexpected error occurred


def validate_token_route():
    try:
        # Parse JSON request body
        data = request.get_json()

        # Extract required fields from the request
        access_token = data.get('token')
        uid = data.get('uid')
        full_name = data.get('full_name')

        if not access_token or not uid or not full_name:
            return jsonify({"error": "Missing required fields"}), 400

        # Validate the token
        reason_code = validate_access_token(access_token, uid, full_name)

        if reason_code == 0:
            return jsonify({"message": "Token is valid"}), 200
        else:
            return jsonify({"error": "Token is invalid", "reason_code": reason_code}), 401

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500