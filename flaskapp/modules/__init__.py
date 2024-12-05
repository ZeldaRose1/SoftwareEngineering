"""Application factory for flask applications"""

#!/usr/bin/python3

import flask
# from modules.database import db
from modules.routing import assign_routes, db


def create_app(config_object=None):
    """Create application for other .py files"""
    # Initialize flask app
    app = flask.Flask(__name__, template_folder='../templates')

    if config_object is not None:
        # Read configuration from file
        app.config.from_object(config_object)
    else:
        # Load in default configuration manually

        # Initialize secret key for session management
        app.secret_key = "CHANGEME"
        # Configure SQLite db, relative to app instance folder
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

    # Moved db.init_app(app) to different location for testing
    # # Initialize database connection
    db.init_app(app)

    # # Create database file if it does not exist
    with app.app_context():
        db.create_all()
    
    # Wire routing to the application
    assign_routes(app)

    # Return the final product
    return app
