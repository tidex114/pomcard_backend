import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import request, jsonify
from models import RegisteringUser
from extensions import db
from datetime import datetime

# Configure your email settings
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


# Generate a random 6-digit code
def generate_reset_code():
    return random.randint(100000, 999999)


# Send the reset code via email
def send_verification_email(email, verification_code):
    subject = "Email Verification Code"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; text-align: center;">
        <img src="cid:pomcard_logo" alt="Pomcard Logo" height="60" style="margin-bottom: 20px;">
        <div style="display: inline-block; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
            <h2 style="color: #333;">Email Verification Code</h2>
            <p style="font-size: 16px;">Please use the code below to verify your email address:</p>
            <p style="font-size: 20px; color: #ED4747; font-weight: bold;">{verification_code}</p>
            <p style="font-size: 16px;">This code is valid for 10 minutes. If you did not request this, please ignore this email or contact support if you have concerns.</p>
            <p style="font-size: 14px; color: #666;">Thank you,<br><strong>Pomfret Card Team</strong></p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    msg.attach(MIMEText(body, 'html'))

    with open(r'pomcard_logo.png', 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<pomcard_logo>')
        msg.attach(img)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# Function to send email verification code
def verify_email_code():
    try:
        data = request.get_json()
        email = data.get('email')

        # Check if email is provided
        if not email:
            return jsonify({'message': 'Email is required'}), 400

        # Look up the registering user in the registration attempts table
        registering_user = RegisteringUser.query.filter_by(email=email).first()

        if not registering_user:
            return jsonify({'message': 'User not found in registration attempts'}), 404

        # Generate a new verification code
        verification_code = generate_reset_code()
        registering_user.generated_code = verification_code
        registering_user.code_creation_time = datetime.now()
        db.session.commit()

        # Send the verification code via email
        if send_verification_email(email, verification_code):
            return jsonify({'message': 'Verification code sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send verification code'}), 500

    except Exception as e:
        # Log the exception and return a server error
        print(f"Error during email code verification: {e}")
        return jsonify({'message': 'An error occurred during email code verification'}), 500
