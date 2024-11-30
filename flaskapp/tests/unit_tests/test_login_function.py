"""Test login() to ensure functionality"""

from flaskapp.modules.data_functions import login_function

def test_login_function_valid(app):
    """Checks function to ensure it returns a valid skey"""
    # Enable context to ensure proper db connection
    with app.app_context():
        # Call function
        skey = login_function("iregardie", "pomegranate")
        # Check return data type
        assert skey is not None
        # Check skey length
        assert len(skey) == 80


def test_login_function_invalid(app):
    """Verify None output on failed login"""
    # Enable context to ensure proper db connection
    with app.app_context():
        # Call function
        skey = login_function("acrowley", "therion")
        # Check return data type
        assert skey is None
