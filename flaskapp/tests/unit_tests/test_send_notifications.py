"""Validates functionality of send_notifications function"""

import pytest
import modules

from modules.data_functions import send_notifications

def test_send_notifications(mocker):
    """Verify send_notifications will work with valid input using mocker"""

    mocker.patch("modules.data_functions.send_email")

    # Send notification
    send_notifications()

    # Validate send_email is called
    #modules.data_functions.send_email.assert_called_once_with("clean dishes", "chores", "clean dishes before lunch", "oath@breaker.com")
    modules.data_functions.send_email.assert_called()
    #smtplib.SMTP_SSL.return_value.__enter__.return_value.sendmail.assert_called_once_with("uconotificaitons@gmail.com", "mock@pytest.com", """From: uconotificaitons@gmail.com\nTo: mock@pytest.com\nSubject: New car!\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nMIME-Version: 1.0\n\nCategory:  Major purchases\nNote: Your car is dying\n""")

    assert True
