"""tests for python routing"""

from flask import session

def test_root_path(client):
    """Check validity of root path"""
    # Pull root of webpage
    response = client.get("/")
    # Check for the proper title
    assert b"<title>Reminder App Login</title>" in response.data
    # Check for a functional webpage
    assert response.status_code == 200

    # Check for inputs
    # Proper login information
    post_res = client.post("/", data={
        "username": "iregardie",
        "password": "pomegranate"
    })
    # Check if call is successful
    assert post_res.status_code == 200
    # Check if we have the proper welcome message
    assert "My Schedule" in post_res.get_data(as_text=True)
    # Check that the reminders are displaying properly
    assert "chores" in post_res.get_data(as_text=True)
    assert "clean dishes" in post_res.get_data(as_text=True)


def test_invalid_path(client):
    """Verifies proper 404 handling"""
    # Pull bad url
    response = client.get("/random_page_that_doesnt_exist")
    assert response.status_code == 404


def test_create_user_path(client):
    """Checks for create user page"""
    # Pull root of webpage
    response = client.get("/create_user")
    # Check for the proper title
    assert b"<title>Create User</title>" in response.data
    # Check for a functional webpage
    assert response.status_code == 200

    # Check for valid response for proper data
    post_res = client.post("/create_user",data={
        "username": "test",
        "password": "password",
        "email": "email@email.com"
    })
    # Client should be redirected (302)
    assert post_res.status_code == 302

    # Check for invalid response for improper data
    post_res = client.post("/create_user",data={
        "username": "test",
        "password": None,
        "email": "email@email.com"
    })
    # Client should remain on same page
    assert post_res.status_code == 200


def test_welcome_route(client):
    """Tests the welcome page functionality"""
    # Set skey to something that's in the database
    with client.session_transaction() as session:
        session['skey'] = 'a'

    # Pull response
    response = client.post("/welcome", follow_redirects=True)
    # assert response.status_code == 200
    assert "chores" in response.get_data(as_text=True)

    # Test for category search
    fil_res = client.post("/welcome", follow_redirects=True, data={
        "keyword": "chores"
    })
    assert fil_res.status_code == 200
    assert 'chores' in fil_res.get_data(as_text=True)
    assert 'taxes' not in fil_res.get_data(as_text=True)

    # Test task name search
    fil_res2 = client.post("/welcome", follow_redirects=True, data={
        "keyword": "taxes"
    })
    assert fil_res2.status_code == 200
    assert 'taxes' in fil_res2.get_data(as_text=True)
    assert 'chores' not in fil_res2.get_data(as_text=True)


def test_create_task_route(client):
    """Tests the create_task functionality"""
    # Set skey to something that's in the database
    with client.session_transaction() as session:
        session['skey'] = 'a'

    # Pull response
    response = client.post("/create_task", follow_redirects=True)
    assert response.status_code == 200
    # Check to make sure the Jinja form is reading the category
    assert "chores" in response.get_data(as_text=True)

