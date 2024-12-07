"""Test create_user()"""

import pytest
# Import function to test
from modules.data_functions import create_user_function
from modules.__init__ import db
from modules.database import Users

def test_create_user_function_valid(app):
    """Checks create_user_function() with valid input"""
    # Open app_context to initialize in-memory database
    with app.app_context():
        # Call function to insert user
        create_user_function("new_user", 'pass', 'hi@aol.com')
        # Pull user that we just pushed to the database
        result = db.session.query(Users.user_name).where(Users.user_name == "new_user").all()
        # Check for a single return value
        assert len(result) == 1
        # Check the user_name matches what we pushed
        assert result[0][0] == 'new_user'


def test_create_user_function_invalid(app):
    """Checks create_user_function() with valid input"""
    # Open app_context to initialize in-memory database
    with app.app_context():
        # Call function to insert user
        create_user_function("new_user", None, 'hi@aol.com')
        # Pull user that we just pushed to the database
        result = db.session.query(Users.user_name).where(Users.user_name == "new_user").all()
        # Check for a single return value
        assert len(result) == 0
