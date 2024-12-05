"""Test application factory"""

from modules import config
from modules import create_app

def test_application_factory():
    """
    Tests for the default setting to not be set to testing
    and for the testing environment to be set to testing
    """
    # Ensure the non-testing app is not configured for testing
    assert not create_app().testing
    # Ensure the testing app is configured for testing
    assert create_app(config.TestingConfig()).testing
