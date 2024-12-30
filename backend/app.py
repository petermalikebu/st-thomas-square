from flask import Flask, g
from pymongo import MongoClient


def get_db():
    """Lazy initialization of MongoDB client."""
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017/')
        g.db = client['peter']
    return g.db


def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    @app.teardown_appcontext
    def teardown_db(exception):
        """Close the MongoDB client at the end of the request."""
        db = g.pop('db', None)
        if db is not None:
            db.client.close()

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
