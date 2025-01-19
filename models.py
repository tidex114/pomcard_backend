from datetime import datetime
from extensions import db  # Import db from extensions.py
from werkzeug.security import generate_password_hash, check_password_hash  # For hashing

class RegisteringUser(db.Model):
    __tablename__ = 'registration_attempts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    generated_code = db.Column(db.String(6), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)  # Store the hashed password
    is_active = db.Column(db.Boolean, default=False)
    code_creation_time = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set the password."""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<RegisteringUser {self.email}>"

# New Users table for finalized user data after successful registration
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    gmail = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    pin_hash = db.Column(db.String(128), nullable=True)
    pin_salt = db.Column(db.String(128), nullable=True)  # New column for storing the salt
    finishedRegistration = db.Column(db.Boolean, default=False)
    password_salt = db.Column(db.String(128), nullable=True)
    isFrozen = db.Column(db.Boolean, default=False)
    public_key = db.Column(db.Text, nullable=True)  # Column to store the user's public key

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the user's hashed password."""
        return check_password_hash(self.password_hash, password)

    def set_pin(self, pin):
        """Generate a salt, hash the user's PIN, and store them."""
        salt = bcrypt.gensalt()
        self.pin_salt = salt.decode('utf-8')
        self.pin_hash = bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')

    def check_pin(self, pin):
        """Check the user's hashed PIN using the stored salt."""
        if not self.pin_salt:
            return False
        hashed_pin = bcrypt.hashpw(pin.encode('utf-8'), self.pin_salt.encode('utf-8')).decode('utf-8')
        return hashed_pin == self.pin_hash

    def __repr__(self):
        return f"<User {self.gmail}>"
class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Session user_id={self.user_id} token={self.session_token}>"


class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    reset_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<PasswordReset email={self.email} reset_code={self.reset_code}>"

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    gmail = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')

    def __repr__(self):
        return f"<Report id={self.id} gmail={self.gmail} status={self.status}>"


class RefreshToken(db.Model):
    __tablename__ = 'refresh_token'

    refresh_token = db.Column(db.String(512), primary_key=True)  # Make refresh_token the primary key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    device_model = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
