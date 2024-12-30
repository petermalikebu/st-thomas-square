from flask import Flask
from pymongo import MongoClient


def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    # MongoDB setup
    client = MongoClient('mongodb://localhost:27017/')
    app.db = client['peter']

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
