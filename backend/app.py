from flask import Flask, g
from pymongo import MongoClient
from .routes import main  # Import the main blueprint

def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    # MongoDB setup
    client = MongoClient('mongodb://localhost:27017/')
    app.config['MONGO_DB'] = client['peter']  # Replace 'peter' with your database name
    app.db = app.config['MONGO_DB']  # Set db as an attribute of the Flask app

    @app.before_request
    def before_request():
        """Set the database connection to g for the current request."""
        g.db = app.db  # Set db to g.db for use in each request

    @app.teardown_request
    def teardown_request(exception=None):
        """Optional: Close the database connection if needed after each request."""
        db = getattr(g, 'db', None)
        if db is not None:
            # No explicit action needed for MongoDB (connection is automatically managed)
            pass

    # Register Blueprints
    app.register_blueprint(main)  # Register the main blueprint

    return app
