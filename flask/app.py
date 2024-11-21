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
    
    # Pull top number from the remiders table
    rid = db.session.execute(sa.text(
        f"""
            SELECT MAX(r.reminder_id) + 1
            FROM
                reminders AS r
                INNER JOIN sessions AS s
                    ON r.user_id = s.user_id
            WHERE
                s.session_key = '{skey}'
        """
    )).fetchone()[0]

    # If there is no entry in the table default to 1.
    if rid == 0 or rid is None:
        rid = 1

    # Make reminder object from inputs
    r = Reminders(reminder_id = rid, user_id=uid, task_name=rname, category=cat, reminder_date=rdate)
    
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


def delete_reminder_function(skey, rid):
    """
    Deletes reminder from the reminders table

    Parameters:
        skey: session key to pull user_id
        r_id: reminder id for the reminder to delete

    Returns:
        True if the reminder is deleted, False otherwise
    """
    print("delete_reminder_function() called.")
    try:
        # Execute delete query
        delete_query=f"""
                DELETE
                FROM reminders
                WHERE reminders.reminder_id IN (
                    SELECT reminder_id FROM reminders AS r
                        INNER JOIN sessions AS s
                        ON r.user_id = s.user_id
                    WHERE
                        s.session_key='{skey}'
                        AND r.reminder_id={rid}
                )
            """
        print("delete_reminder_function() query:\n" + delete_query)
        db.session.execute(sa.text(delete_query))
        # Commit the delete
        db.session.commit()
        # Print success statement
        print("delete_reminder_function() successful")
        return True
    except Exception as e:
        # Print failure statement
        print("delete_reminders_function() failed\n" + str(e))
        return False


def update_reminder_function(skey, r_id, r_name, r_cat, r_date):
    """
    Updates parts of a reminder based on given parameters

    Parameters:
        skey: session key for current session.
        r_id: id of reminder to update
        r_name: name to update or None if no update is requested
        r_cat: category to update or None if no update is requested
        r_date: new date for reminder or None if no update is requested
    
    Returns:
        True if update succeeds or False otherwise
    """
    print("update_reminder_function() called")

    # Start compilation of SQL queries
    update_query = """
        UPDATE reminders
        SET 
    """
    
    # Check for variables to update
    
    # Boolean to control comma structure
    first_nn_var = True

    # Adjust query for r_name
    if r_name is not None and r_name != '':
        update_query += f"task_name='{r_name}'"
        first_nn_var = False
    
    # Adjust query for r_cat
    if r_cat is not None and r_cat != '':
        if first_nn_var:
            update_query += f"category='{r_cat}'"
            first_nn_var = False
        else:
            update_query += f", category='{r_cat}'"

    # Adjust query for r_date
    if r_date is not None and r_date != '':
        if first_nn_var:
            update_query += f"reminder_date = '{r_date}'"
            first_nn_var = False
        else:
            update_query += f", reminder_date = '{r_date}'"
    
    # Finalize the update query
    update_query += f" WHERE reminder_id = {r_id}"

    # Debug print statement
    # print("update_reminder_function() update_query:\n" + update_query)

    try:
        # Run query
        db.session.execute(sa.text(update_query))
        # Commit changes
        db.session.commit()
        # Print tracing statement
        print("update_query_function() executed successfully")
        # Return True to indicate a successful push.
        return True
    except Exception as e:
        # Print tracing statement
        print("update_query_function() failed:\n" + str(e))
        # Return False to indicate a failed push.
        return False


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
    reminder_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    task_name = sa.Column(sa.String, nullable=False)
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
@app.route("/welcome/<skey>", methods=["GET", "POST"])
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
        WHERE s.session_key = '{skey}'
        ORDER BY r.reminder_date
        """
    )).all()
    print("welcome() reminders:")
    print(reminders)

    # Define urls for create and update reminders
    create_rem_url = url_for("create_reminder", skey=skey)
    update_rem_url = url_for("update_reminder", skey=skey)

    return render_template(
        'welcome.html',
        username=un,
        reminders=reminders,
        skey=skey,
        create_rem_url=create_rem_url,
        update_rem_url=update_rem_url
    )


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


# Build view for updating a reminder
@app.route("/update_reminder/<skey>", methods=["GET", "POST"])
def update_reminder(skey):
    """
    Page to update reminders

    Params:
        skey: session_key to verify session and pull data from db
    
    Returns:
        HTML view
    """
    # Debugging statement
    print("update_reminder() called")

    # Verify session
    if not verify_login(skey):
        # If session is invalid return to login page
        return redirect(url_for("root"))
    
    # Pull parameters from form if the form has filled
    try:
        r_id = request.form['r_id']
    except:
        r_id = None    
    try:
        r_name = request.form['r_name']
    except:
        r_name = None
    try:
        r_cat = request.form['r_cat']
    except:
        r_cat = None
    try:
        r_date = request.form['r_date']
    except:
        r_date = None
    try:
        update = request.form['update']
    except:
        update = None
    try:
        delete = request.form['delete']
    except:
        delete = None
    
    # Debugging
    print("update_reminder() update:" + str(update))
    print("update_reminder() delete:" + str(delete))
    # Success!! We can pull different buttons.

    # Check if delete function is called with enough information
    if r_id is not None and delete == "Delete":
        delete_reminder_function(skey, r_id)
    
    # Check for update function:
    if r_id is not None and update=="Update" and (
        r_name is not None or r_cat is not None or r_date is not None):
        update_reminder_function(skey, r_id, r_name, r_cat, r_date)   

    # Pull list of reminders. This should be after the update operation
    reminders = db.session.execute(sa.text(
        f"""
        SELECT r.reminder_id, r.task_name, r.category, r.reminder_date
        FROM reminders AS r INNER JOIN sessions AS s
        ON r.user_id = s.user_id
        WHERE s.session_key = '{skey}'
        ORDER BY r.reminder_date
        """
    )).all()
    print("update_reminder() reminders:")
    print(reminders)
    
    # if r_id is None:
    # print("update_reminder() r_id is None")
    return render_template('update_reminder.html', skey=skey, reminders=reminders)
    # else:
    #     # TODO: update this after logic is built out.
    #     print("update_reminder() is not None")
    #     return render_template('update_reminder.html', skey=skey, reminders=reminders)
        
@app.route("/search/<skey>", methods=["GET", "POST"])
def rem_search(skey):
    """
    Create page view to display, sort, and filter reminders.
    """



print('script finished')

if __name__ == "__main__":
        app.run()
