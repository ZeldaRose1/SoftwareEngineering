from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for
from flask import session
import sqlalchemy as sa

# from modules.data_functions import create_session
from modules.data_functions import login_function
from modules.data_functions import create_user_function
from modules.data_functions import verify_login
from modules.data_functions import create_task_function
from modules.data_functions import db
from modules.data_functions import send_notifications

def assign_routes(app):
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


    @app.route("/welcome/delete/<rid>", methods=["GET", "POST"])
    @app.route("/welcome", methods=["GET", "POST"])
    def welcome(rid=None):
        """Renders welcome template with queried data"""
        # Print tracing statement
        print("welcome() function called")
        # Pull session key from session
        skey = session.get('skey')
        # Verify login
        if not verify_login(skey):
            return redirect(url_for('root'))

        # Define reminder query
        rem_query = f"""
            SELECT
                reminder_id, task_name,
                category, task_date
            FROM reminders AS r
            WHERE r.user_id IN (
                SELECT user_id
                FROM sessions
                WHERE sessions.session_key = '{skey}'

        """

        # Check if there is a search term and modify the query accordingly
        try:
            keyword = request.form["keyword"]
        except Exception:
            keyword = None

        if keyword is not None and keyword != '':
            rem_query += f"""
                AND (
                    r.category LIKE '%{keyword}%' OR
                    r.task_name LIKE '%{keyword}%'
                )
            """

        # Start notification loop
        # send_notifications()

        # Add final closing parenthesis regardless of keyword
        rem_query += "\n)"

        # Pull list of reminders
        try:
            reminders = db.session.execute(sa.text(rem_query)).all()
            # Print results if successful
            print("welcome() pull reminders:")
            print(reminders)
        except Exception as e:
            print("welcome() reminder pull failed\n" + str(e))
            # Make empty list to prevent NameErrors
            reminders = []

        # Handle delete query
        del_query = f"DELETE FROM reminders WHERE reminder_id = '{rid}'"
        print('del_query:\n' + del_query)
        if rid is not None:
            try:
                # Execute delete query
                db.session.execute(sa.text(del_query))
                # Commit changes
                db.session.commit()
                # Trace statement for debugging
                # print(f"Reminder no: {rid} deleted")
                # Clear url to avoid recursion
                return redirect(url_for("welcome"))
            except Exception as e:
                # Tracing statement for debugging
                print(f"Reminder no: {rid} could not be deleted")
                # Clear url
                return redirect(url_for("welcome"))

        return render_template("welcome.html", reminders=reminders, skey=skey)


    # @app.route("/create_task/<skey>", methods=["GET", "POST"])
    @app.route("/create_task", methods=["GET", "POST"])
    def create_task():
        """Return HTML for reminder creation page and handle creation"""
        # Tracing statement
        print("Create_task() called")
        # Pull skey from session
        skey = session.get("skey")

        # Pull variables from form
        if request.method == "POST":
            t_name = request.form.get("taskName", None)
            new_cat = request.form.get("CategoryName", None)
            use_existing_cat = request.form.get("enableCategory", False)
            reuse_category = request.form.get("Category", None)
            tdate = request.form.get("datePicker", None)
            task_note = request.form.get("AddNote", None)
            reminder_time = request.form.get("Time", None)
            if reminder_time == "Option1":
                reminder_time = timedelta(minutes=-5) + \
                    datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
            if reminder_time == "Option2":
                reminder_time = timedelta(minutes=-15) + \
                    datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
            if reminder_time == "Option3":
                reminder_time = timedelta(minutes=-30) + \
                    datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
            if reminder_time == "Option4":
                reminder_time = timedelta(
                    hours=-1) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
            if reminder_time == "Option5":
                reminder_time = timedelta(
                    hours=-24) + datetime.strptime(tdate, "%Y-%m-%dT%H:%M")
            reminder_b = request.form.get("enableTime", False)
            email_b = request.form.get("Email", False)
            sms_b = request.form.get("SMS", False)
        else:
            t_name = None
            new_cat = None
            use_existing_cat = None
            reuse_category = None
            tdate = None
            task_note = None
            reminder_time = None
            reminder_b = None
            email_b = None
            sms_b = None

        # Verify boolean values are read as boolean
        if reminder_b == "on":
            reminder_b = True
        if email_b == "on":
            email_b = True
        if sms_b == "on":
            sms_b = True

        # We have automatic testing so trace statements are unneeded
        # print(t_name)
        # print(new_cat)
        # print(use_existing_cat)
        # print(reuse_category)
        # print(tdate)
        # print(task_note)
        # print("reminder_time:" + str(reminder_time))
        # print("reminder_b:\t" + str(reminder_b))
        # print(note_bool)
        # print(email_b)
        # print(sms_b)

        # If reuse category is checked reassign the category var
        if use_existing_cat is True and reuse_category != "":
            new_cat = reuse_category

        # Check reminder is enabled; if not disable email and sms
        if not reminder_b:
            email_b = False
            sms_b = False

        # Pull all categories in database
        categories = db.session.execute(
            sa.text("""SELECT DISTINCT category FROM reminders""")).all()
        print("Categories:")
        print(categories)

        # Check for all necessary values to create a reminder
        if ((new_cat is not None and new_cat != "") and
                    (t_name is not None and t_name != "") and
                    (tdate is not None)
                ):
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
                return redirect(url_for("welcome"))

        return render_template("create_task.html", skey=skey, category=categories)


    @app.route("/view_task/<rid>", methods=["GET"])
    def view_task(rid):
        """Create view for a given task."""
        # Pull session key from session
        skey = session.get('skey')
        # Verify login
        if not verify_login(skey):
            return redirect(url_for('root'))

        # Pull task from database
        task = db.session.execute(sa.text(
            f"""
                SELECT
                    category,
                    task_name,
                    task_date,
                    note,
                    reminder_dtm
                FROM
                    reminders
                WHERE reminder_id = {rid}
            """
        )).all()

        # Render template with task details.
        return render_template("view_task.html", task=task)

    @app.route("/update_task/<rid>", methods=["GET", "POST"])
    def update_task(rid):
        """Handles updating a specific task by reminder ID."""
        # Pull session key
        skey = session.get("skey")

        # Verify login is active
        if not verify_login(skey):
            return redirect(url_for("root"))

        # Pull variables
        if request.method == "POST":
            category = request.form.get("CategoryName", "")
            task_date = request.form.get("datePicker", "")
            email = request.form.get("Email", False)
            sms = request.form.get("SMS", False)
            note = request.form.get("AddNote", "")
            try:
                # Save query
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
                # Execute query
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
                # Save changes to database
                db.session.commit()
                # If update succeeds, return to welcome page
                return redirect(url_for("welcome"))
            except Exception as e:
                # If update fails print error message
                print(f"Error updating task: {str(e)}")
                # Return to update task page
                return render_template("update_task.html", task=None)
        try:
            # Query to pull reminder values from reminder id
            task_query = sa.text(
                """
                SELECT reminder_id, category, task_name, task_date, note, reminder_dtm
                FROM reminders
                WHERE reminder_id = :rid
                """
            )
            # Pull reminder
            task = db.session.execute(task_query, {"rid": rid}).fetchone()
        except Exception as e:
            # Print error message if one exists
            print(f"Error fetching task details: {str(e)}")
            # Assign task to a variable to avoid NameError
            task = None

        if task is None:
            print(f"Task with ID {rid} not found!")
            return redirect(url_for("welcome"))

        # Load HTML page
        return render_template("update_task.html", task=task)
