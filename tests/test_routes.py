from flask import json
from server.models.models import Users, Camera

def test_heartbeat(test_client):
    cameraID = 2
    response = test_client.get("/heartbeat/" + str(cameraID))
    response_data = json.loads(response.get_data(as_text=True))

    cam = Camera.query.filter_by(id = cameraID).first()
    user_primary_cam = Users.query.filter_by(id=cam.user_id).first().primary_camera
    
    assert response_data['camera_id'] == cam.id
    assert response_data['mode'] == cam.mode.value
    assert response_data['is_primary'] == (user_primary_cam == cameraID)
    assert response_data['encodings'] == None

def test_logout(test_client):
    response = test_client.get('/logout', follow_redirects=True)
    
    # Check that there was one redirect response.
    assert len(response.history) == 1
    
    # Check that the second request was to the login page.
    assert response.request.path == "/login"

def test_valid_login(test_client):
    response = test_client.post('/login', data=dict(
            email="apitest@gmail.com",
            password="123456"
        ), follow_redirects=True)

    # Check that there was one redirect response.
    assert len(response.history) == 1
    
    # Check that the second request was to the home page.
    assert response.request.path == "/"

def test_invalid_password_login(test_client):
    response = test_client.post('/login', data=dict(
            email="apitest@gmail.com",
            password="654321"
        ), follow_redirects=True)

    assert b'Invalid email/password' in response.data

def test_invalid_email_login(test_client):
    response = test_client.post('/login', data=dict(
            email="asdf@gmail.com",
            password="123456"
        ), follow_redirects=True)

    assert b'Invalid email/password' in response.data

def test_invalid_signup(test_client):
    response = test_client.post('/signup', data=dict(
            name="test",
            email="apitest@gmail.com",
            password="123456"
        ), follow_redirects=True)

    assert b'A user already exists with that email!' in response.data
