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


def create_reminder_function(un, skey, uid, rname, cat, rdate):
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
    print("create_reminder_function() called")

    print("create_reminder_function() rdate type:\t" + str(type(rdate)))
    print("create_reminder_function() rdate type:\t" + str(rdate))
    # Convert rdate into python datetime object
    rdate = datetime.strptime(rdate, "%Y-%m-%dT%H:%M")
    print("create_reminder_function() rdate type:\t" + str(type(rdate)))
    
    # Make reminder object from inputs
    r = Reminders(user_id=uid, task_name=rname, category=cat, reminder_date=rdate)
    
    # Start database operations
    try:
        # Push reminder to Reminders table
        db.session.add(r)
        # Commit changes to the database
        db.session.commit()
        # Refresh welcome page to reflect changes to the table
        return True
    except Exception as e:
        # Print error statement
        print("Error creating reminder:\n" + str(e))
        # Return to welcome page
        return False


# <codecell> function definitions
def login_function(username, password):
    """
    Queries the database and redirects to the appropriate location
    if the user exists or does not.
    """
    print("login_function() called")
    
    try:
        result = db.session.query(Users.user_id).filter((Users.user_name == username) & (Users.password == password)).all()
        print("login_function() query results:")
        print(result)
    except Exception as e:
        print("login_function() error:\n" + str(e))
        return None
    
    print("login_function() result:")
    print(result)
    if len(result) != 0:
        uid = result[0][0]
    else:
        print("login_function(): User not found")
        return None
    
    # print("Login check query returned " + str(len(result)) + " rows")
    
    # Create session and return the session key
    skey = create_session(uid)
    return skey


def create_user_function(username, password, email=None):
    """
    Creates a new user in the USERS table.
    """
    user = Users(user_name=username, password=password, email=email)
    try:
        db.session.add(user)
        db.session.commit()
        return login()
    except:
        return create_user()


def verify_login(skey):
    """
    Queries the database for a matching session.
    Checks for existing session in database

    Params:
        skey: session key to check against database
    
    Returns:
        boolean: True if session is verified False otherwise
    """
    # Pull session end from the Sessions table.
    result = db.session.query(Sessions.session_end).filter(Sessions.session_key==skey).all()
    # Verify that there is at least one row
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
    """Table to track user information"""
    __tablename__ = "users"

    user_id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_name = sa.Column(sa.String, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String)
    isadmin = sa.Column(sa.Boolean, default=False)


class Reminders(db.Model):
    """Table to track reminders"""
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
    if un is None or pw is None:
        # Render template
        return redirect(url_for("root"))
    
    # Tracing statement for debugging
    print(f"login() username read is\t\t'{un}'")

    # Create session and pull skey
    if request.method == "POST" and un != "" and un is not None:
        # Check db for username and password. Return session id if match else None
        skey = login_function(un, pw)

        # Check if session is established and pull reminders for user
        if skey is not None:
            print("login() successfully created session")
            
            # Pull reminders to render the welcome template
            reminders = db.session.query(  # Select columns
                    Reminders.user_id, Reminders.task_name,
                    Reminders.category, Reminders.reminder_date
                ).select_from(Sessions).join(  # Join to Sessions as filter
                    Reminders, Reminders.user_id == Sessions.user_id
                ).where(  # Ensure only current session is queried
                    Sessions.session_key==skey
                ).all()

        else:
            print("login_function() in login did not find matching un and pw")
            return redirect(url_for("root"))

    if skey is None:
       return redirect(url_for("root"))
    
    # Render the welcome page
    return welcome(skey)

@app.route("/", methods=["GET", "POST"])
def root():
    print("root() called")
    return render_template("login.html")


# Rework the welcome page
@app.route("/welcome", methods=["GET", "POST"])
def welcome(skey=None):
    """
    Verify session, pull parameters, render template

    Params:
        skey: session key for the session used to verify login
    """
    print("welcome() called")

    # validate session
    if not verify_login(skey):
        print("welcome() could not verify session")
        return redirect("root")
    
    # Pull username
    un = db.session.execute(sa.text(
        f"""
        SELECT u.user_name FROM users AS u INNER JOIN sessions AS s
        ON u.user_id = s.user_id
        WHERE s.session_key = '{skey}'
        """
    )).fetchone()[0]
    print("welcome() username=" + str(un))

    # Pull reminder list
    reminders = db.session.execute(sa.text(
        f"""
        SELECT r.task_name, r.category, r.reminder_date
        FROM reminders AS r INNER JOIN sessions AS s
        ON r.user_id = s.user_id
        WHERE s.user_id = '{skey}'
        """
    )).all()
    print("welcome() reminders:")
    print(reminders)

    # Define urls for create and update reminders
    create_rem_url = url_for("create_reminder", skey=skey)
    # update_rem_url = url_for("update_reminders", skey=skey)

    return render_template(
        'welcome.html',
        username=un,
        reminders=reminders,
        skey=skey,
        create_rem_url=create_rem_url
        # TODO: uncomment following line after update_reminder implemented
        # update_rem_url=update_rem_url
    )


# @app.route("/welcome", methods=["GET", "POST"])
# @app.route("/welcome/<skey>", methods=["GET", "POST"])
# def welcome(username=None):
#     # Tracing function for debugging
#     print("welcome(username, skey) function called")
#     print("welcome(username, skey) username:\t" + str(username))
    
#     # Pull skey from url
#     try:
#         skey = request.get_data('skey', None)
#     except:
#         skey = None
#     print("welcome(username, skey) skey:\t" + str(skey))
    
#     # Check method
#     print("welcome() method = " + request.method)

#     print(request.data)
#     # Ensure the user has an active session
#     verify_login(skey)
    
#     # Pull list of tasks associated with this user
#     reminders = db.session.query(  # Select columns
#         Reminders.user_id, Reminders.task_name,
#         Reminders.category, Reminders.reminder_date
#     ).select_from(Sessions).join(  # Join to Sessions as filter
#         Reminders, Reminders.user_id == Sessions.user_id
#     ).where(  # Ensure only current session is queried
#         Sessions.session_key==skey
#     ).all()

#     # Tracing statement for debugging
#     print("welcome() reminder list:")
#     print(reminders)
    
#     # Render template
#     return render_template("welcome.html", username=username, reminders=reminders, skey=skey)


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


@app.route("/create_reminder/<skey>", methods=["GET", "POST"])
def create_reminder(skey):
    """ Render page for reminder creation form """
    # Debugging statement
    print("create_reminder() method called")
    print("create_reminder method:\t" + str(request.method))
    print("create_reminder() skey = " + str(skey))

    # TODO: Verify how skey is handled (reminder or kwarg)
    if not verify_login(skey):
        return redirect("root")

    # Pull un and uid from skey
    result = db.session.query(  # Select columns
        Users.user_name, Users.user_id
    ).select_from(Sessions).join(  # Join to Sessions as filter
        Users, Sessions.user_id == Users.user_id
    ).where(  # Ensure only current session is queried
        Sessions.session_key == skey
    ).all()

    # Parse reminders from result (should be redundant w verify_login above)
    if len(result) == 0:
        raise Exception("create_reminder():\tNo session found")
    elif len(result) > 1:
        raise Exception("create_reminder():\tMultiple sessions found")
    else:
        un = result[0][0]
        uid = result[0][1]

    # Read inputs from form to create a new reminder
    if request.method == "POST":
        try:
            rname = request.form['rname']
            cat = request.form['cat']
            rdate = request.form['rdate']
        except Exception as e:
            print("create_reminder() error:\t" + str(e))
            rname = None
            cat = None
            rdate = None
    
    # Upload the reminder to the database
    if request.method == "POST" and rname is not None and cat is not None and rdate is not None:
        upd_result = create_reminder_function(un, skey, uid, rname, cat, rdate)
        print("create_reminder() upd_result=" + str(upd_result))
        if not upd_result:
            print("Reminder creation failed")
            return redirect(url_for("create_reminder", skey=skey))
        else:
            print("create_reminder() success!")
            return welcome(skey)
    else:
        print("create_reminder() insufficient data to attempt creation")
        return render_template("create_reminder.html", skey=skey)


print('script finished')

if __name__ == "__main__":
        app.run()
