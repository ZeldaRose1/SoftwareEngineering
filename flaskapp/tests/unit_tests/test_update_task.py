import pytest
from datetime import datetime
from modules.__init__ import db
from modules.data_functions import update_tasks, fetch_task, create_task_function
from modules.database import Reminders

from sqlalchemy import text  # Import `text` from SQLAlchemy


def test_fetch_task_valid(app):
    """Test fetch_task() with a valid reminder ID."""
    with app.app_context():
        # Create a new task
        task = create_task_function(
            'a',
            'pet care',
            'feed ibis',
            '2024-12-01T12:00',
            '2024-12-01T12:00',
            True,
            False,
            'Ibis need to eat before we leave for the day.'
        )

        # Verify reminders table has entry
        result = db.session.query(Reminders.task_name).where(
            Reminders.category == "pet care"
        ).all()

        task = Reminders.query.filter_by(task_name="feed ibis").first()
        assert task is not None


def test_fetch_task_invalid(app):
    """Test fetch_task() with an invalid reminder ID."""
    with app.app_context():
        task, error = fetch_task(999, db)  # Reminder ID 999 does not exist
        assert task is None
        assert error is None  # Should gracefully return no error


def test_update_tasks_valid(app):
    """Test update_tasks() with valid input."""
    with app.app_context():
        # Create a new task
        task = create_task_function(
            'a',
            'pet care',
            'feed ibis',
            '2024-12-01T12:00',
            '2024-12-01T12:00',
            True,
            False,
            'Ibis need to eat before we leave for the day.'
        )

        # Verify reminders table has entry
        result = db.session.query(Reminders.task_name).where(
            Reminders.category == "pet care"
        ).all()

        task = Reminders.query.filter_by(task_name="feed ibis").first()

        # Prepare updated request data
        request_data = {
            "Category": "Updated Category",
            "datePicker": "2024-12-07T15:00",  # datetime-local format
            "Email": False,
            "SMS": True,
            "AddNote": "Updated note",
        }

        # Test update_tasks
        success, error = update_tasks(2, request_data, db)
        assert success is True
        assert error is None

        # Verify the update
        task, _ = fetch_task(2, db)
        assert task["category"] == "Updated Category"
        assert task["task_date"] == "2024-12-07T15:00"
        assert task["email"] is 0
        assert task["sms"] is 1
        assert task["note"] == "Updated note"


def test_update_tasks_invalid(app):
    """Test update_tasks() with an invalid reminder ID."""
    with app.app_context():
        # Prepare invalid request data
        request_data = {
            "Category": "Invalid Category",
            "datePicker": "2024-12-07T15:00",
            "Email": False,
            "SMS": True,
            "AddNote": "Invalid update",
        }

        # Test update_tasks
        # Reminder ID 999 does not exist
        success, error = update_tasks(999, request_data, db)
        assert success is False
        assert "Error fetching task" in error
