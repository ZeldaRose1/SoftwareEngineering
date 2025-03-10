# First party imports
from datetime import datetime
from email.message import EmailMessage
import glob
import os
import random
import string
import ssl
import smtplib
import threading

# Third party imports
import sqlalchemy as sa
from flask import render_template, redirect, url_for
from modules.database import db, Users, Sessions
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger


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


def send_email(name, category, note, email):
    """Send email based on reminder table values"""
    # Save hardcoded values for group email
    email_sender = 'uconotificaitons@gmail.com'
    email_password = 'oqya mzhd rvmf apoi'
    email_receiver = email

    # Save parameters
    subject = name
    # Debugging by sending variables
    body = f"""Category:  {category}\nNote: {note}"""

    # Initialize email object and set email parameters
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Create context
    context = ssl.create_default_context()

    # Use login context manager
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        # Login to gmail
        smtp.login(email_sender, email_password)
        # Send email
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def update_tasks(rid, request_data, db):
    """Update a task based on reminder ID and form data."""
    task, error = fetch_task(rid, db)
    if not task:
        return False, f"Error fetching task: {error}"

    category = request_data.get("Category")
    if category == "new":
        category = request_data.get("NewCategoryName")
        if not category:
            return False, "New category name cannot be empty."
    category = category or task['category']

    task_date = request_data.get("datePicker") or task['task_date']
    email = request_data.get("Email", task['email'])
    sms = request_data.get("SMS", task['sms'])
    note = request_data.get("AddNote") or task['note']

    try:
        update_query = sa.text(
            """
            UPDATE reminders
            SET category = :category,
                task_date = :task_date,
                email = :email,
                sms = :sms,
                note = :note
            WHERE reminder_id = :rid
            """
        )
        db.session.execute(
            update_query,
            {
                "category": category,
                "task_date": task_date,
                "email": email,
                "sms": sms,
                "note": note,
                "rid": rid,
            },
        )
        db.session.commit()
        return True, None
    except Exception as e:
        return False, str(e)

def fetch_task(rid, db):
    """Fetch a task based on reminder ID."""
    try:
        task_query = sa.text(
            """
            SELECT reminder_id, category, task_name, task_date, note,
                   reminder_dtm, email, sms
            FROM reminders
            WHERE reminder_id = :rid
            """
        )
        task = db.session.execute(task_query, {"rid": rid}).fetchone()

        if task:
            task = {key: value for key, value in task._mapping.items()}

            if task['task_date']:
                try:
                    if "T" not in task['task_date']:
                        task['task_date'] = datetime.strptime(
                            task['task_date'], '%Y-%m-%d %H:%M:%S'
                        ).strftime('%Y-%m-%dT%H:%M')
                except ValueError:
                    print(f"Invalid task_date format: {task['task_date']}")
                    task['task_date'] = None

        return task, None
    except Exception as e:
        return None, str(e)

def send_notifications(debug = False, date_time_format = '%Y-%m-%d %H:%M:%S'):

    # Query for notifications
    notifications_query = """
        SELECT *
        FROM reminders join users
            ON reminders.user_id = users.user_id
    """

    #use threading and the stored database
    if (debug == False):
        """Send notifications"""
        # Start repeated timer for sending notifications
        threading.Timer(15.0, send_notifications).start()

        # Find path to database
        db_rel_path = glob.glob('**/database.db', recursive=True)[0]
        print(db_rel_path)
        
        # Create sqlalchemy engine to access database independently
        engine = sa.create_engine(f"sqlite:///{db_rel_path}")
        # Open connection to database
        if os.path.exists(db_rel_path):
            con = engine.connect()
        else:
            print("Database does not exist")
            print("Current working directory: " + os.getcwd())
            return
    #use no thread and the database in RAM
    else:
        con = db.session

    # Pull all notifications
    notifications = con.execute(sa.text(notifications_query)).all()
    # Loop over all reminders in reminders table
    for reminder in notifications:
        if reminder[5] != 'None':
            if reminder[5] is not None and datetime.strptime(reminder[5], date_time_format) < datetime.now():
                # Check reminders boolean
                if reminder[6] == 1:
                    # Send email with the specific values from the table
                    send_email(reminder[2], reminder[3], reminder[8], reminder[12])

                    # Turn email notification off after sending
                    disable_notification = f"""
                        UPDATE reminders
                        SET email = 0
                        WHERE reminder_id = {reminder[1]}
                    """

                    # Execute query
                    con.execute(sa.text(disable_notification))
                    # Save change to database.
                    con.commit()


def edit_user(skey, uname, pw, email):
    """
    Update entry in Users table with given parameters

    Parameters:
        skey: session_key to validate user identity
        uname: username to update Users table entry with
        pw: password to update Users table entry with
        email: email to update Users table entry with
    
    Returns:
        True if push successful, False otherwise
    """
    # Write update query in steps
    query = "UPDATE users\nSET\n\t"

    # Set variable to help handle commas
    comma_needed = False
    if (uname is not None and uname != ''):
        query += f"user_name='{uname}'"
        comma_needed = True
    
    # Handle logic for password section
    if (pw is not None and pw != ''):
        # Adjust for commas
        if comma_needed:
            query += ",\n"
        query += f"password='{pw}'"
        comma_needed = True
    
    # Handle logic for email section
    if (email is not None and email != ''):
        # Adjust for commas
        if comma_needed:
            query += ",\n"
        query += f"email='{email}'"

    # Add where clause
    query += f"\nWHERE user_id IN (\
        SELECT user_id FROM sessions WHERE session_key='{skey}')"

    print(query)
    
    # Update the user information
    try:
        # Execute query
        db.session.execute(sa.text(query))
        # Commit changes
        db.session.commit()
        # Return true flag for a successful push
        return True
    except Exception as e:
        # Print error message
        print(f"Error in edit_user:\t{e}")
        # Return false flag for failed push
        return False