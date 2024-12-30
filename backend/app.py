from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Import the db from the models file
from backend.models import db  # Assuming you have a models.py file that defines db


def create_app():
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Flask-Migrate with db object from models
    migrate = Migrate(app, db)

    # Initialize the database
    db.init_app(app)

    # Example model (could also be in models.py)
    class Menu(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80), nullable=False)
        type = db.Column(db.String(80), nullable=False)

    # Create tables if they don't exist (can be moved to a migration script later)
    with app.app_context():
        db.create_all()

    # Register blueprints after app initialization
    from backend.routes import main  # Adjust path based on your file structure
    app.register_blueprint(main)

    return app
