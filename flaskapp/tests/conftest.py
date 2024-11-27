"""Fixtures for pytest"""

#!/usr/bin/python

import os
# from flask_sqlalchemy import SQLAlchemy
# from app import app as app
from modules.config import TestingConfig

import pytest
from sqlalchemy import text
from flaskapp.modules.__init__ import create_app, db
from flaskapp.modules.database import db

# global app

@pytest.fixture(autouse=True)
def app():
    """Fixture to create temporary database"""
    # Make app and configuration
    app = create_app(TestingConfig())

    # Insert values into testing database
    with app.app_context():
        db.session.execute(text("""
            INSERT INTO users (user_name, password, email)
            VALUES ('iregardie', 'pomegranate', 'oath@breaker.com')
        """))
        db.session.commit()

    yield app

    # Clean up after tests
    db.session.remove()
    db.drop_all()


@pytest.fixture(autouse=True)
def client(app):
    """create test client"""
    return app.test_client()


@pytest.fixture(autouse=True)
def runner(app):
    """Create test cli runner"""
    return app.test_cli_runner()


@pytest.fixture
def x():
    x = "hello"
    return x
