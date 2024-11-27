"""Create database for use in testing and development code"""

#!/usr/bin/python3

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase  # For creating table definitions


class Base(DeclarativeBase):
    """Class exists to create tables"""
    pass


# Initialize database
db = SQLAlchemy(model_class=Base)
# Initialize app with db extension (does not create database.db yet,
# but does create instance folder)
# db.init_app(app)


class Users(db.Model):
    """Table to track user data"""
    __tablename__ = "users"

    user_id = sa.Column(
        sa.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        unique=True
    )
    user_name = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String)
    isadmin = sa.Column(sa.Boolean, default=False)


class Sessions(db.Model):
    """Table to track user logins"""
    __tablename__ = 'sessions'
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )

    session_key = sa.Column(
        sa.String,
        primary_key=True,
        nullable=False,
        unique=True
    )

    session_start = sa.Column(sa.DateTime, nullable=False)
    session_end = sa.Column(sa.DateTime, nullable=True)


class Reminders(db.Model):
    """Track reminder and task data"""
    __tablename__ = "reminders"
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False
    )

    reminder_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    task_name = sa.Column(sa.String)
    category = sa.Column(sa.String)
    task_date = sa.Column(sa.DateTime)
    reminder_dtm = sa.Column(sa.DateTime)
    email = sa.Column(sa.Boolean)
    sms = sa.Column(sa.Boolean)
    note = sa.Column(sa.String)
