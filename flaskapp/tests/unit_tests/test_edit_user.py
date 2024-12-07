"""Validates functionality of edit_user"""

import pytest
from sqlalchemy import text

from modules.data_functions import edit_user
from modules.__init__ import create_app, db

def test_edit_user_name_valid(app):
    """Validate functionality of edit_user() when only username is changed."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', 'regardiei', 'pomegranate', 'oath@breaker.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "regardiei"
    assert u[0][2] == "pomegranate"
    assert u[0][3] == "oath@breaker.com"


def test_edit_password_valid(app):
    """Validate functionality of edit_user() when only password is changed."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', 'iregardie', 'pompom', 'oath@breaker.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "iregardie"
    assert u[0][2] == "pompom"
    assert u[0][3] == "oath@breaker.com"


def test_edit_email_valid(app):
    """Validate functionality of edit_user() when only password is changed."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', 'iregardie', 'pomegranate', 'stella@matutina.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "iregardie"
    assert u[0][2] == "pomegranate"
    assert u[0][3] == "stella@matutina.com"


def test_edit_all_valid(app):
    """Validate functionality of edit_user() when only password is changed."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', 'ireg', 'pompom', 'stella@matutina.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "ireg"
    assert u[0][2] == "pompom"
    assert u[0][3] == "stella@matutina.com"


def test_edit_null_pw(app):
    """Validate functionality of edit_user() when password is None."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', 'regardiei', None, 'oath@breaker.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "regardiei"
    assert u[0][2] == "pomegranate"
    assert u[0][3] == "oath@breaker.com"


def test_edit_null_uname(app):
    """Validate functionality of edit_user() when username is None."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', None, 'warpigs', 'oath@breaker.com')

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "iregardie"
    assert u[0][2] == "warpigs"
    assert u[0][3] == "oath@breaker.com"


def test_edit_null_email(app):
    """Validate functionality of edit_user() when username is None."""
    with app.app_context():
        # Edit database and save result
        check = edit_user('a', "jtkirk", 'usse', None)

    # Assert edit_user returned a true value
    assert check is True

    # Pull database values to ensure no unintended changes happened
    with app.app_context():
        u = db.session.execute(text(
            "SELECT * FROM users WHERE user_id = 1"
        )).all()

    assert u[0][1] == "jtkirk"
    assert u[0][2] == "usse"
    assert u[0][3] == "oath@breaker.com"
