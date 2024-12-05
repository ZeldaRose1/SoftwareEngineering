"""Fixtures for pytest"""

#!/usr/bin/python

# import os
from modules.config import TestingConfig

import pytest
from sqlalchemy import text
from modules.__init__ import create_app, db
# from modules.database import db

@pytest.fixture(autouse=True)
def app():
    """Fixture to create temporary database"""
    # Make app and configuration
    app = create_app(TestingConfig())

    # Insert user into testing database
    with app.app_context():
        db.session.execute(text("""
            INSERT INTO users (user_name, password, email)
            VALUES ('iregardie', 'pomegranate', 'oath@breaker.com')
        """))
        db.session.commit()
    
    # Insert session into testing database
    with app.app_context():
        db.session.execute(text("""
            INSERT INTO sessions (user_id, session_key, session_start)
            VALUES (1, 'a', STRFTIME("%Y-%m-%dT%H:%M", '2024-11-27T11:10'))
        """))
        db.session.commit()
    
    # Insert reminders into testing database
    with app.app_context():
        db.session.execute(text("""
            INSERT INTO reminders (
                user_id,
                reminder_id,
                task_name,
                category,
                task_date,
                reminder_dtm,
                email,
                sms,
                note
            )
            VALUES (
                1,
                1,
                'clean dishes',
                'chores',
                STRFTIME("%Y-%m-%dT%H:%M", '2024-12-01T12:00'),
                STRFTIME("%Y-%m-%dT%H:%M", '2024-12-01T11:00'),
                True,
                False,
                'clean dishes before lunch'
            )
        """))
        db.session.execute(text("""
            INSERT INTO reminders (
                user_id,
                reminder_id,
                task_name,
                category,
                task_date,
                reminder_dtm,
                email,
                sms,
                note
            )
            VALUES (
                1,
                2,
                'file taxes',
                'finances',
                STRFTIME("%Y-%m-%dT%H:%M", '2024-12-01T12:00'),
                STRFTIME("%Y-%m-%dT%H:%M", '2024-12-01T11:00'),
                True,
                False,
                'file taxes for grandparents'
            )
        """))
        db.session.commit()

    yield app

    # Clean up after tests
    with app.app_context():
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
