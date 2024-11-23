#!/usr/bin/python3

from datetime import datetime, timedelta
import os
import random
import string

import flask
from flask import render_template, request, redirect, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase  # For creating table definitions


# <codecell> Class definitions
class Base(DeclarativeBase):
    """Class exists to create tables"""
    pass


def create_session(uid):
    """
    Creates a new session in the session table corresponding to the user id
    """
    sk = ''.join(random.choice(string.ascii_lowercase) for i in range(80))
    ses = Sessions(
        user_id=uid,
        session_key=sk,
        session_start=datetime.now(),
        session_end=None
    )
    try:
        db.session.add(ses)
        db.session.commit()
        print('Session created')
        return sk
    except Exception as e:
        print(str(e) + "\n\nCould not create session")


# <codecell> function definitions
def login_function(username, password):
    """
    Queries database for matching user and creates a session.
    Returns the skey if session create else None
    """
    print("login_function() called")
    
    # result = db.session.execute(db.select(Users).where(Users.user_name==username).where(Users.password==password)).all()
    # result = Users.query.filter_by(user_name=username, password=password).all()
    result = db.session.query(Users.user_id).filter((Users.user_name == username) & (Users.password == password)).all()
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
    
    user=Users(user_name=username, password=password, email=email)
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
    result = db.session.query(Sessions.session_end).filter(Sessions.session_key == skey).all()
    
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


# <codecell> Initialize items and set parameters
# Initialize database
db = SQLAlchemy(model_class=Base)

# Initialize flask app
app = flask.Flask(__name__)
# Initialize secret key for session management
app.secret_key = "CHANGEME"

# Configure SQLite db, relative to app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

# Initialize app with db extension (does not create database.db yet, but does create instance folder)
db.init_app(app)

# <codecell> Define tables as sub-classes of db.Model
class Users(db.Model):
    __tablename__ = "users"

    user_id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_name = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String)
    isadmin = sa.Column(sa.Boolean, default=False)


class Sessions(db.Model):
    """Table to track user logins"""
    __tablename__ = 'sessions'
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False)
    session_key = sa.Column(sa.String, primary_key=True, nullable=False, unique=True)
    session_start = sa.Column(sa.DateTime, nullable=False)
    session_end = sa.Column(sa.DateTime, nullable=True)


class Reminders(db.Model):
    __tablename__ = "reminders"
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False)
    reminder_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    task_name = sa.Column(sa.String)
    category = sa.Column(sa.String)
    task_date = sa.Column(sa.DateTime)
    reminder_dtm = sa.Column(sa.DateTime)
    email = sa.Column(sa.Boolean)
    sms = sa.Column(sa.Boolean)
    note = sa.Column(sa.String)


# Initialize database and create tables
with app.app_context():
    db.create_all()

# <codecell> Start programming the webpage routing

@app.route("/", methods=["GET", "POST"])
def root():
    """Render login page and manage inputs to other pages"""
    try:
        un = request.form['username']
        pw = request.form['password']
    except:
        un = None
        pw = None
    
    if un is not None and pw is not None:
        # Pull session key
        skey = login_function(un, pw)
        # Store session key in flask session.
        session['skey'] = skey
        return welcome()
    else:
        return render_template("login.html")


@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    """Takes input from request forms and adds new user to database."""

    # TODO: Implement a creation success message
    
    # Attempt to pull values from variables
    try:
        un = request.form['username']
        pw = request.form['password']
        email = request.form['email']
    except:
        un = None
        pw = None
        email = None
    
    # Check if input is filled in
    if un is not None and pw is not None and email is not None:
        # Call function to create the user
        return create_user_function(un, pw, email)
    else:
        # Render html template
        return render_template("create_user.html")
    
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    """Renders welcome template with queried data"""
    # Print tracing statement
    print("welcome() function called")
    # Pull session key from session
    skey = session.get('skey')
    # Verify login
    if not verify_login(skey):
        return redirect(url_for('root'))
    
    # Pull list of reminders
    try:
        reminders = db.session.execute(sa.text(
            f"""
                SELECT
                    reminder_id, task_name,
                    category, task_date
                FROM reminders AS r
                WHERE r.user_id IN (
                    SELECT user_id
                    FROM sessions
                    WHERE sessions.session_key = '{skey}'
                )
            """
        )).all()
        
        # Print results if successful
        print("welcome() pull reminders:")
        print(reminders)
    except Exception as e:
        print("welcome() reminder pull failed\n" + str(e))
        # Make empty list to prevent NameErrors
        reminders = []

    # Pull username
    try:
        # Run query
        un = db.session.execute(sa.text(
            f"""
                SELECT
                    u.user_name
                FROM
                    users AS u
                WHERE u.user_id IN (
                    SELECT user_id
                    FROM sessions AS s
                    WHERE s.session_key = '{skey}'
                )
            """
        )).all()[0][0]
        # Print username if pull is successful
        print("welcome() username:\t" + str(un))
    except Exception as e:
        print("welcome() could not pull username:\n" + str(e))
        # Set None to prevent NameError
        un = None

    # Print statements for debugging.
    print("welcome() reminders:")
    print(reminders)
    print(f"welcome() username:\t{str(un)}")

    return render_template("welcome.html", reminders=reminders, username=un, skey=skey)


# @app.route("/create_task/<skey>", methods=["GET", "POST"])
@app.route("/create_task", methods=["GET", "POST"])
def create_task():
    """Return HTML for reminder creation page and handle creation"""
    # Tracing statement
    print("Create_task() called")
    # Pull skey from session
    skey = session.get("skey")
    
    # Pull variables from form
    try:
        t_name = request.form["taskName"]
    except:
        t_name = None
    try:
        new_cat = request.form["CategoryName"]
    except:
        new_cat = None
    try:
        use_existing_cat = request.form["enableCategory"]
        use_existing_cat = True
    except:
        use_existing_cat = False
    try: 
        reuse_category = request.form["Category"]
    except:
        reuse_category = None
    try:
        tdate = request.form["datePicker"]
    except:
        tdate = None
    try:
        task_note = request.form["AddNote"]
    except:
        task_note = None
    try:
        reminder_time = request.form["Time"]
        if reminder_time == "Option1":
            reminder_time = timedelta(minutes = -5) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
        if reminder_time == "Option2":
            reminder_time = timedelta(minutes = -15) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
        if reminder_time == "Option3":
            reminder_time = timedelta(minutes = -30) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
        if reminder_time == "Option4":
            reminder_time = timedelta(hours = -1) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
        if reminder_time == "Option5":
            reminder_time = timedelta(hours = -24) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
    except Exception as e:
        print("Error fixing reminder time:\n" + str(e))
        reminder_time = None
    try:
        reminder_b = request.form["enableTime"]
        reminder_b = True
    except:
        reminder_b = False
    try:
        note_bool = request.form["enableTime"]
        note_bool = True
    except:
        note_bool = False
    try:
        email_b = request.form["Email"]
        if email_b is not None:
            email_b = True
    except:
        email_b = False
    try:
        sms_b = request.form["SMS"]
        if sms_b is not None:
            sms_b = True
    except:
        sms_b = False

    print(t_name)
    print(new_cat)
    print(use_existing_cat)
    print(reuse_category)
    print(tdate)
    print(task_note)
    print("reminder_time:" + str(reminder_time))
    print("reminder_b:\t" + str(reminder_b))
    print(note_bool)
    print(email_b)
    print(sms_b)

    # If reuse category is checked reassign the category var
    if use_existing_cat is True and reuse_category != "":
        new_cat = reuse_category
    
    # Check reminder is enabled; if not disable email and sms
    if not reminder_b:
        email_b = False
        sms_b = False
    
    # Pull all categories in database
    categories = db.session.execute(sa.text("""SELECT DISTINCT category FROM reminders""")).all()
    print("Categories:")
    print(categories)

    # Check for all necessary values to create a reminder
    if ((new_cat is not None and new_cat != "") and
        (t_name is not None and t_name != "") and
        (tdate is not None)
    ):
        # TODO: update function call to match new function variables.
        if create_task_function(
            skey,
            new_cat,
            t_name,
            tdate,
            reminder_time,
            email_b,
            sms_b,
            task_note
        ):
            return redirect(url_for("welcome", skey=skey))
    
    return render_template("create_task.html", skey=skey, category=categories)


print('script finished')

if __name__ == "__main__":
        app.run()
 
