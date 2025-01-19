import jwt
import os
import datetime
from flask import request, jsonify
from sqlalchemy.orm.exc import NoResultFound
from models import RefreshToken, db
import bcrypt
from services.generate_jwt import generate_jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')
AUDIENCE = os.getenv('AUDIENCE')
ISSUER = os.getenv('ISSUER')

def refresh_access_token():
    try:
        # Step 1: Get the refresh token from the request
        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            print("Debug: Refresh token is missing")
            return jsonify({"error": "Refresh token is required"}), 400

        # Step 2: Decode the refresh token
        decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"], audience=AUDIENCE, issuer=ISSUER)
        user_id = decoded_token["sub"]
        aud = decoded_token["aud"]
        iss = decoded_token["iss"]
        device_info = decoded_token["device_info"]

        print(f"Debug: Decoded token - user_id: {user_id}, aud: {aud}, iss: {iss}")

        # Step 3: Retrieve the hashed refresh token from the database
        token_record = db.session.query(RefreshToken).filter_by(user_id=user_id).first()

        if not token_record:
            print("Debug: No matching refresh token found in the database")
            return jsonify({"error": "Invalid or expired refresh token"}), 401

        if token_record.expires_at < datetime.datetime.utcnow():
            print("Debug: Refresh token has expired in the database")
            return jsonify({"error": "Invalid or expired refresh token"}), 401

        stored_hashed_token = token_record.refresh_token.encode()  # Ensure the stored hash is in bytes
        print(f"Debug: Retrieved hashed refresh token: {stored_hashed_token}")

        # Step 4: Verify the bcrypt hash
        if not bcrypt.checkpw(refresh_token.encode(), stored_hashed_token):
            print("Debug: Refresh token hash does not match")
            return jsonify({"error": "Invalid refresh token"}), 401

        # Step 5: Validate claims
        if aud != AUDIENCE or iss != ISSUER:
            print(f"Debug: Token claims do not match - aud: {aud}, iss: {iss}")
            return jsonify({"error": "Token claims do not match"}), 401

        if device_info != token_record.device_model:
            print(f"Debug: Device info does not match - {device_info} vs {token_record.device_model}")
            return jsonify({"error": "Device info does not match"}), 401

        # Step 6: Generate a new access token
        new_access_token = generate_jwt(user_id, decoded_token["name"], device_info=token_record.device_model)

        # Step 7: Update the database
        token_record.created_at = datetime.datetime.utcnow()
        token_record.expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        db.session.commit()

        print("Debug: New access token generated and database updated")

        return jsonify({
            "access_token": new_access_token  # Include only if rotating tokens
        }), 200

    except jwt.ExpiredSignatureError:
        print("Debug: Refresh token has expired")
        return jsonify({"error": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError as e:
        print(f"Debug: Invalid refresh token - {e}")
        return jsonify({"error": "Invalid refresh token"}), 401
    except NoResultFound:
        print("Debug: No matching refresh token found")
        return jsonify({"error": "No matching refresh token found"}), 401
    except Exception as e:
        print(f"Debug: Unexpected error - {e}")
        return jsonify({"error": str(e)}), 500