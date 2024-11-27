"""Configuration file for applications"""

#!/usr/bin/python3
import random
import string


class Config:
    """Abstract class for configuration files"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Configuration for main development"""
    # Set Secret key to randomized string
    SECRET_KEY = ''.join(
        random.choice(string.ascii_lowercase)
        for i in range(20)
    )
    # Set database instance
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"


class TestingConfig(Config):
    """Configuration file for testing"""
    # Set database instance
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Set secrete_key to a consistent value for testing
    SECRET_KEY = 'TEST'
    # Set TESTING to True
    TESTING = True
