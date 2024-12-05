"""Tests create_task_function"""
import pytest
import sqlalchemy as sa

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


def test_create_task_function_invalid_skey(app):
    """Validates create_task_function() with invalid skey"""
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


def test_create_task_function_valid_partial(app):
    """Validates create_task_function() with some parameters"""
    # Initialize database connection
    with app.app_context():
        # Create new task and save result
        bool_check = create_task_function(
            'a',
            sa.sql.null(),
            'null_test',
            '2024-12-01T12:00',
            '2024-12-01T12:00',
            sa.sql.null(),
            sa.sql.null(),
            sa.sql.null()
        )
        # Assert correct value returned
        assert bool_check is True

        # Verify reminders table has entry
        result = db.session.query(Reminders.task_name).where(
            Reminders.task_name == 'null_test'
        ).all()
        
        # Verify there is only one result (based on fixture)
        assert len(result) == 1
        # Verify the task_name matches what we put in
        assert result[0][0] == "null_test"
