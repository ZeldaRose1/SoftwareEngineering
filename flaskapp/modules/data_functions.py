from datetime import datetime, timedelta
# import os
import random
import string

import sqlalchemy as sa
from flask import render_template, redirect, url_for

# from modules.config import ProductionConfig
# from modules.__init__ import create_app
from flaskapp.modules.database import db, Users, Sessions
# from flaskapp.modules.__init__ import db

def create_session(uid):
    """
    Create a new session in the session table corresponding to the user id
    """
    # Validate user id exists in user table
    u_check = db.session.query(Users.user_id).\
        where(Users.user_id == uid).all()
    if len(u_check) == 0:
        raise ValueError("User ID not found in user table")

    # Generate random string for session
    sk = ''.join(random.choice(string.ascii_lowercase) for i in range(80))
    # Create session object
    ses = Sessions(
        user_id=uid,
        session_key=sk,
        session_start=datetime.now(),
        session_end=None
    )
    try:
        # Push to database
        db.session.add(ses)
        db.session.commit()
        print('Session created')
        return sk
    except Exception as e:
        print(str(e) + "\n\nCould not create session")
        return None


# <codecell> function definitions
def login_function(username, password):
    """
    Queries database for matching user and creates a session.
    Returns the skey if session create else None
    """
    print("login_function() called")

    # result = db.session.execute(db.select(Users).where(Users.user_name==username).where(Users.password==password)).all()
    # result = Users.query.filter_by(user_name=username, password=password).all()
    result = db.session.query(Users.user_id).filter(
        (Users.user_name == username) & (Users.password == password)).all()
    print("login_function()results:")
    print(result)

    if len(result) != 0:
        uid = result[0][0]
    else:
        uid = None

    print("login_function() uid:\t" + str(uid))

    if uid is not None:
        skey = create_session(uid)
        print("Login successful")
        return skey
    else:
        print("Login failed")
        return None


def create_user_function(username, password, email):
    """
    Creates a new user in the USERS table.
    """
    # Validate username
    if username is None or username == "":
        print("create_user_function() invalid username:\t" + str(username))
        return render_template("create_user.html")
    # Validate password
    if password is None or password == "":
        print("create_user_function() invalid password:\t" + str(password))
        return render_template("create_user.html")
    # Validate email
    if email is None or email == "":
        print("create_user_function() invalid email:\t" + str(email))
        return render_template("create_user.html")

    user = Users(user_name=username, password=password, email=email)
    try:
        # Add user to users table.
        db.session.add(user)
        # Commit update.
        db.session.commit()
        print("User creation succeeded.")
        return redirect(url_for("root"))
    except:
        print("User creation failed")
        return render_template("create_user.html")


def verify_login(skey):
    """
    Queries the database for a matching session.
    Checks for existing session in database and
    returns true if verified else redirects to route
    """
    print("verify_login() called")
    # Pull session from sessions table
    result = db.session.query(Sessions.session_end).filter(
        Sessions.session_key == skey).all()

    print("verify_login() result:" + str(result))
    # Verify there is at least one row
    if len(result) == 0:
        # Trace statements for debugging
        print("session could not be verified. Result:\n")
        print(result)
        # Clean memory to avoid carryover
        del result
        # Return user to login if they do not have a session
        return False
    else:
        # Verify that the session has not expired
        if result[0][0] is None:
            # Tracing statement
            print("session verified")
            # Clean memory to avoid carryover
            del result
            # TODO: rework this. Bad idea to exploit duck typing
            return True
        else:
            # Session exists, but has a non-None value in session_end
            print("Session existed, but was expired")
            # Clean memory to avoid carryover
            del result
            return False


def create_task_function(skey, category, name, task_date, rem_date, email, sms, note):
    """
    Create a new reminder from input

    Params:
        skey: session key for current session
        category: Category to append to Reminders
        name: reminder name to append to Reminders
        task_date: DateTime of the event
        rem_date: DateTime to send reminder
        email: True to send reminder by email
        sms: True to send reminder by sms
        note: Note for extra detail on task

    Returns:
        True if push successful
        False if push fails
    """
    print("create_task_function() called.")
    print(f"skey = '{skey}'")
    print(f"category = '{category}'")
    print(f"name = '{name}'")
    print(f"task_date = '{task_date}'")
    print(f"rem_date = '{rem_date}'")
    print(f"email = '{email}'")
    print(f"sms = '{sms}'")

    # Pull user id
    try:
        uid = db.session.execute(sa.text(
            f"SELECT user_id FROM sessions WHERE session_key = '{skey}'"
        )).all()[0][0]
        # Print output to verify uid.
        print(f"User id pulled from skey = '{uid}'")
    except Exception as e:
        print("could not pull uid:\n" + str(e))
        # Session could not be verified; terminate function with fail
        return False

    # Pull reminder id
    try:
        r_seq = db.session.execute(sa.text(
            "SELECT MAX(reminder_id) + 1 FROM reminders"
        )).all()[0][0]
        print(f"New id for reminder: '{r_seq}'")
        if r_seq is None:
            r_seq = 1
    except Exception as e:
        print("Could not pull reminder_id\n" + str(e))
        # Set 1 as default value
        r_seq = 1

    # Push reminder
    try:
        db.session.execute(sa.text(
            f"""
                INSERT INTO reminders (
                    user_id, reminder_id, task_name,
                    category, task_date, reminder_dtm,
                    email, sms, note
                )
                VALUES (
                    {uid}, {r_seq}, '{name}',
                    '{category}', STRFTIME("%Y-%m-%dT%H:%M", '{task_date}'),
                    STRFTIME("%Y-%m-%d %H:%M:%S", '{rem_date}'),
                    {email}, {sms}, '{note}'
                )
            """
        ))
        db.session.commit()
        print("Reminder successfully created")
        return True
    except Exception as e:
        print("Reminder creation failed:\n" + str(e))
        return False