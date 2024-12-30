from flask import Flask, g
from pymongo import MongoClient


def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    # MongoDB setup
    client = MongoClient('mongodb://localhost:27017/')
    app.config['MONGO_DB'] = client['peter']

    @app.before_request
    def before_request():
        """Set the database connection to g for current request."""
        g.db = app.config['MONGO_DB']

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
