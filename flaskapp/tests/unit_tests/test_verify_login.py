"""Verify session has a session_key that has not expired"""
import pytest


from flaskapp.modules.data_functions import verify_login
from flaskapp.modules.__init__ import db

def test_verify_login_valid(app):
    """Asserts verify_login returns True for existing session"""
    # Set skey to something that's in the database
    with app.app_context():
        check = verify_login('a')
        assert check is True


def test_verify_login_invalid(app):
    """Asserts verify_login returns True for existing session"""
    # Set skey to something that's in the database
    with app.app_context():
        check = verify_login('abcdefghijklmnopqrstuvwxyz')
        assert check is False
