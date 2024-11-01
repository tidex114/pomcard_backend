import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from flask import request, jsonify
from models import User, PasswordReset
from extensions import db
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure your email settings
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Generate a random 6-digit code
def generate_reset_code():
    return random.randint(100000, 999999)

# Send the reset code via email
def send_reset_email(to_email, reset_code):
    subject = "Did you request a password reset?"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="cid:pomcard_logo" alt="Pomcard Logo" height="60">
        </div>
        <div style="max-width: 60%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
            <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
            <p style="font-size: 16px;">We noticed a request to reset the password for your Pomcard account. If this was you, use the code below to proceed with the password reset:</p>
            <div style="background-color: #ffffff; padding: 20px; border: 1px solid #ddd; border-radius: 8px; text-align: center; margin: 20px 0;">
                <p style="font-size: 20px; color: #ED4747; font-weight: bold;"><strong>{reset_code}</strong></p>
            </div>
            <p style="font-size: 16px;">This code is valid for 10 minutes. If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
            <br>
            <p style="font-size: 14px; color: #666;">Thank you,<br><strong>Pomfret Card Team</strong></p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'html'))

    with open(r'pomcard_logo.png', 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<pomcard_logo>')
        msg.attach(img)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Function to handle password reset requests
def password_reset():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email or not email.endswith('@pomfret.org'):
            return jsonify({'message': 'Invalid email address'}), 400

        user = User.query.filter_by(gmail=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        reset_code = generate_reset_code()
        expiration_time = datetime.now() + timedelta(minutes=10)

        # Create or update the password reset entry
        password_reset_entry = PasswordReset.query.filter_by(email=email).first()
        if password_reset_entry:
            password_reset_entry.reset_code = reset_code
            password_reset_entry.expires_at = expiration_time
        else:
            password_reset_entry = PasswordReset(email=email, reset_code=reset_code, expires_at=expiration_time)
            db.session.add(password_reset_entry)

        db.session.commit()

        if send_reset_email(email, reset_code):
            return jsonify({'message': 'Password reset code sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send password reset code'}), 500

    except Exception as e:
        print(f"Error during password reset: {e}")
        return jsonify({'message': 'An error occurred during password reset'}), 500

# Function to handle password reset verification
def verify_reset_code():
    try:
        data = request.get_json()
        email = data.get('email')
        reset_code = data.get('reset_code')

        if not email or not reset_code:
            return jsonify({'message': 'Email and reset code are required'}), 400

        reset_entry = PasswordReset.query.filter_by(email=email, reset_code=reset_code).first()
        if not reset_entry:
            return jsonify({'message': 'Invalid reset code'}), 400

        if datetime.now() > reset_entry.expires_at:
            return jsonify({'message': 'Reset code has expired'}), 400

        return jsonify({'message': 'Reset code verified successfully'}), 200

    except Exception as e:
        print(f"Error during reset code verification: {e}")
        return jsonify({'message': 'An error occurred during reset code verification'}), 500
