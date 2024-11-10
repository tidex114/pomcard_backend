import os

from flask import Flask, session
from extensions import db
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance with the app
db.init_app(app)

# Import the routes after app and db are initialized
from routes.auth_routes import auth_routes
app.register_blueprint(auth_routes)

# Example route where you set the session permanent flag
@app.before_request
def make_session_permanent():
    session.permanent = True  # Ensure session expires after the set time

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before the first request
    app.run(host='0.0.0.0', port=5001, debug=True)