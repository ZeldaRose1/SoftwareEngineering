"""Validates functionality of send_notifications function"""

import pytest
import modules

from modules.data_functions import send_notifications
from modules.__init__ import db
from modules.database import Reminders

def test_send_notifications(app, mocker):
    """Verify send_notifications will work with valid input using mocker"""

    mocker.patch("modules.data_functions.send_email")

    with app.app_context():

        # Verify email is set for first reminder
        task = Reminders.query.filter_by(email=1).first()
        assert task is not None

        # Send notification
        send_notifications(True, '%Y-%m-%dT%H:%M')

        # Validate send_email is called
        #modules.data_functions.send_email.assert_called_with('clean dishes', 'chores', 'clean dishes before lunch', 'oath@breaker.com')
        #modules.data_functions.send_email.assert_called_with('file taxes', 'finances', 'file taxes for grandparents', 'oath@breaker.com')
        modules.data_functions.send_email.assert_called()

        # Verify email is disabled for first notification
        task = Reminders.query.filter_by(email=0).first()
        assert task is not None

    assert True
