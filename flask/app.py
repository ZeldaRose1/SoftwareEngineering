#!/usr/bin/python3

from datetime import datetime
import os
import random
import string

import flask
from flask import render_template, request, redirect
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


def create_reminder(un, skey, uid, rname, cat, rdate):
    """
    Appends new reminder to the Reminders table

    Args:
        un (str): username to return to the welcome page after r creation
        skey (str): session key for login verification
        uid (int): user_id of the current user
        rname (str): reminder_name
        cat (str): category to assign to this reminder
        rdate (datetime): date and time to send reminder

    Returns:
        _type_: _description_
    """
    # Tracing statement for debugging
    print("create_reminder() called")
    
    # Make reminder object from inputs
    r = Reminders(uid, rname, cat, rdate)
    
    # Start database operations
    try:
        # Push reminder to Reminders table
        db.session.add(r)
        # Commit changes to the database
        db.session.commit()
        # Refresh welcome page to reflect changes to the table
        return welcome(un, skey)
    except Exception as e:
        # Print error statement
        print("Error creating reminder:\n" + str(e))
        # Return to welcome page
        return welcome(un, skey)


# <codecell> function definitions
def login_function(username, password):
    """
    Queries the database and redirects to the appropriate location
    if the user exists or does not.
    """
    print("login_function() called")
    
    # result = db.session.execute(db.select(Users).where(Users.user_name==username).where(Users.password==password)).all()
    # result = Users.query.filter_by(user_name=username, password=password).all()
    result = db.session.query(Users.user_id).filter(Users.user_name == username).all()
    uid = result[0][0]
    
    # print("Login check query returned " + str(len(result)) + " rows")
    
    skey = create_session(uid)
    if len(result) == 0:
        return redirect("/")
    else:
        print("Login successful")
        return welcome(username, skey)


def create_user_function(username, password, email=None):
    """
    Creates a new user in the USERS table.
    """
    user=Users(user_name=username, password=password, email=email)
    try:
        db.session.add(user)
        db.session.commit()
        return login()
    except:
        return create_user()


def verify_login(skey):
    """
    Queries the database for a matching session.
    Checks for existing session in database and
    returns true if 
    """
    # Pull session end from the Sessions table.
    result = db.session.query(Sessions.session_end).filter(Sessions.session_key==skey).all()
    # Verify that there is at least one row
    if len(result) == 0:
        # Trace statements for debugging
        print("session could not be verified. Result:\n")
        print(result)
        # Return user to login if they do not have a session
        return redirect("/login")
    else:
        # Verify that the session has not expired
        if result[0][0] is None:
            # Tracing statement
            print("session verified")
            # TODO: rework this. Bad idea to exploit duck typing
            return True
        else:
            # Session exists, but has a non-None value in session_end
            print("Session existed, but was expired")
            return redirect("/login")



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
    user_name = sa.Column(sa.String, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String)
    isadmin = sa.Column(sa.Boolean, default=False)


class Reminders(db.Model):
    __tablename__ = "reminders"
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True, nullable=False)
    task_name = sa.Column(sa.String, primary_key=True)
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

@app.route("/login", methods=["GET", "POST"])
def login():
    # Trace code
    print("login() method called")
    # print(request.method)
    
    # Pull parameters
    try:
        un = request.form['username']
        pw = request.form['password']
    except:
        un = None
        pw = None

    # Check if variables are defined
    if un is not None and pw is not None:
        # Render template
        return render_template("login.html")
    
    # Tracing statement for debugging
    print(f"username read is\t\t'{un}'")

    #
    if request.method == "POST" and un != "" and un is not None:
       return login_function(un, pw)
    else:
       return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
def root():
    print("root() function called")
    return login()


@app.route("/welcome", methods=["GET", "POST"])
# @app.route("/welcome/<skey>")
def welcome(username, skey=None):
    # Tracing function for debugging
    print("welcome(username) function called")
    # Check method
    print("welcome() method = " + request.method)
    # Ensure the user has an active session
    verify_login(skey)
    
    # Pull list of tasks associated with this user
    # TODO: debug and verify this query works
    reminders = db.session.query(  # Select columns
        Reminders.user_id, Reminders.task_name,
        Reminders.category, Reminders.reminder_date
    ).select_from(Sessions).join(  # Join to Sessions as filter
        Reminders, Reminders.user_id == Sessions.user_id
    ).where(  # Ensure only current session is queried
        Sessions.session_key==skey
    ).all()
    
    # Pull parameters
    try:
        # Pull parameters
        rname = request.form['rname']
        cat = request.form['cat']
        rdate = request.form['rdate']
    except:
        # Define parameters as None
        rname = None
        cat = None
        rdate = None
    
    # Check for existing parameters
    if rname is not None and cat is not None and rdate is not None:
        create_reminder(username, skey, rname, cat, rdate)
    
    # Render template
    return render_template("welcome.html", username=username, reminders=reminders)


# @app.route("/hello")
# @app.route("/hello/<name>")
# def hello_name(name=None):
#     return render_template("hello.html", person=name)

@app.route("/create_user", methods=['GET', 'POST'])
def create_user():
    print("create_user() method called")
    print(request.method)
    if request.method == "POST":
        un = request.form['username'].lower()
        pw = request.form['password']
        em = request.form['email']
    if request.method == "POST" and un is not None and un != '':
        return create_user_function(un, pw, em)
    else:
        return render_template("create_user.html")


print('script finished')

if __name__ == "__main__":
        app.run()
 
