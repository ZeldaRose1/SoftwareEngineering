"""Test file for create_sesion"""
import pytest

# Import function to test
from modules.data_functions import create_session

def test_invalid_create_session(app):
    """Tests create_session when called with valid inputs"""
    with app.app_context():
        # No  user with id 150 exists in test_db
        with pytest.raises(ValueError) as r:
            # Give a user id that is not in the database
            create_session(150)


def test_valid_create_session(app):
    """Tests create_session when called with valid inputs"""
    with app.app_context():
        # User id 1 exists. Should return skey
        result = create_session(1)
        assert type(result) is str
        assert len(result) == 80
