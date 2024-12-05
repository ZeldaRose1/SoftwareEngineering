"""Tests create_task_function"""
import pytest

from modules.__init__ import db
from modules.database import Reminders
from modules.data_functions import create_task_function


def test_create_task_function_valid(app):
    """Validates create_task_function() with valid parameters"""
    # Initialize database connection
    with app.app_context():
        # Create new task and save result
        bool_check = create_task_function(
            'a',
            'pet care',
            'feed ibis',
            '2024-12-01T12:00',
            '2024-12-01T12:00',
            True,
            False,
            'Ibis need to eat before we leave for the day.'
        )
        # Assert correct value returned
        assert bool_check is True

        # Verify reminders table has entry
        result = db.session.query(Reminders.task_name).where(
            Reminders.category == "pet care"
        ).all()
        
        # Verify there is only one result (based on fixture)
        assert len(result) == 1
        # Verify the task_name matches what we put in
        assert result[0][0] == "feed ibis"


def test_create_task_function_invalid(app):
    """Validates create_task_function() with valid parameters"""
    # Initialize database connection
    with app.app_context():
        # Create new task and save result
        bool_check = create_task_function(
            'abcdefg666',
            'selfcare',
            'feed ibis',
            '2024-12-01T12:00',
            '2024-12-01T12:00',
            True,
            False,
            'Ibis need to eat before we leave for the day.'
        )
        # Assert correct value returned
        assert bool_check is False

        # Verify reminders table has entry
        result = db.session.query(Reminders.task_name).where(
            Reminders.category == "selfcare"
        ).all()
        
        # Verify there are no results (based on fixture)
        assert len(result) == 0
