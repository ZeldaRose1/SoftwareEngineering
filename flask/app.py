#!/usr/bin/python3

from datetime import datetime
import os
import random
import string

import flask
from flask import render_template, request, redirect, url_for
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
        return redirect(url_for("create_user"))
    # Validate password
    if password is None or password == "":
        print("create_user_function() invalid password:\t" + str(password))
        return redirect(url_for("create_user"))
    # Validate email
    if email is None or email == "":
        print("create_user_function() invalid email:\t" + str(email))
        return redirect(url_for("create_user"))
    
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
        return create_user()


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



# <codecell> Initialize items and set parameters
# Initialize database
db = SQLAlchemy(model_class=Base)

# Initialize flask app
app = flask.Flask(__name__)

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


class Reminders(db.Model):
    __tablename__ = "reminders"
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False)
    reminder_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    task_name = sa.Column(sa.String)
    category = sa.Column(sa.String)
    reminder_date = sa.Column(sa.DateTime)


class Sessions(db.Model):
    """Table to track user logins"""
    __tablename__ = 'sessions'
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False)
    session_key = sa.Column(sa.String, primary_key=True, nullable=False, unique=True)
    session_start = sa.Column(sa.DateTime, nullable=False)
    session_end = sa.Column(sa.DateTime, nullable=True)


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
        return welcome(skey)
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
def welcome(skey):
    """Renders welcome template with queried data"""
    # Print tracing statement
    print("welcome() function called")
    # Verify login
    if not verify_login(skey):
        return redirect(url_for('root'))
    
    # Pull list of reminders
    try:
        reminders = db.session.execute(sa.text(
            f"""
                SELECT
                    reminder_id, task_name,
                    category, reminder_date
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

    return render_template("welcome.html", reminders=reminders, username=un)





print('script finished')

if __name__ == "__main__":
        app.run()
 
