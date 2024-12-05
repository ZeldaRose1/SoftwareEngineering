"""Validates functionality of send_email function"""

import pytest
import smtplib
from modules.data_functions import send_email

def test_send_email(mocker):
    """Verify send_email will work with valid input using mocker"""
    # Mock the smtplib.SMTP_SSL object
    # mock_SMTP_SSL = mocker.MagicMock(name="send_email.smtplib.SMTP_SSL")
    # mocker.patch("smtplib.SMTP_SSL", NEW=mock_SMTP_SSL)
    mocker.patch("smtplib.SMTP_SSL")
    mocker.patch("smtplib.SMTP_SSL.login__enter__.login")
    mocker.patch("smtplib.SMTP_SSL.__enter__.sendmail")

    # Send notification
    send_email("New car!", "Major purchases", "Your car is dying", "mock@pytest.com")

    # Validate smtp_ssl connection is made
    smtplib.SMTP_SSL.return_value.__enter__.return_value.login.assert_called_once_with("uconotificaitons@gmail.com", "oqya mzhd rvmf apoi")
    smtplib.SMTP_SSL.return_value.__enter__.return_value.sendmail.assert_called_once_with("uconotificaitons@gmail.com", "mock@pytest.com", """From: uconotificaitons@gmail.com\nTo: mock@pytest.com\nSubject: New car!\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nMIME-Version: 1.0\n\nCategory:  Major purchases\nNote: Your car is dying\n""")

    assert True
