"""Validates functionality of send_notifications function"""

import pytest
import modules

from modules.data_functions import send_notifications
from modules.__init__ import db
import modules.data_functions
from modules.database import Reminders
from unittest.mock import call

def test_send_notifications(app, mocker):
    """Verify send_notifications will work with valid input using mocker"""

    mocker.patch("modules.data_functions.send_email")

    with app.app_context():

        # Verify email is set for first reminder
        task = Reminders.query.filter_by(email=1).first()
        assert task is not None

        # Send notification
        send_notifications(True, '%Y-%m-%dT%H:%M')

        # Validate send_email is called with the correct arguments
        modules.data_functions.send_email.assert_has_calls([call('clean dishes', 'chores', 'clean dishes before lunch', 'oath@breaker.com'), call('file taxes', 'finances', 'file taxes for grandparents', 'oath@breaker.com')])
        # Ensure send_email was called only twice
        # Send email should not be called for reminder 3 because the reminder date is next year
        # Send email should not be called for reminder 4 because the email boolean is false
        # Send email should not be called for reminder 5 because it has no reminder date
        assert modules.data_functions.send_email.call_count == 2

        # Verify email is disabled for first notification
        task = Reminders.query.filter_by(email=0).first()
        assert task is not None

    assert True
