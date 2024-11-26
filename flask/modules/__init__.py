"""Application factory for flask applications"""

#!/usr/bin/python3

import flask
from .database import db


def create_app(config_filename=None):
    """Create application for other .py files"""
    # Initialize flask app
    app = flask.Flask(__name__, template_folder='../templates')

    if config_filename is not None:
        # Read configuration from file
        app.config.from_pyfile(config_filename)
    else:
        # Load in default configuration manually

        # Initialize secret key for session management
        app.secret_key = "CHANGEME"
        # Configure SQLite db, relative to app instance folder
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

    # Initialize database connection
    db.init_app(app)

    # Create database file if it does not exist
    with app.app_context():
        db.create_all()

    # Return the final product
    return app
