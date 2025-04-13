from app.models.user import User
from werkzeug.security import check_password_hash

def test_user_registration(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password"
    }
    response = client.post('/user/register', json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['message'] == 'User created successfully'
    
def test_duplicate_registration(client, registered_user):
    payload = {
        "username": "testuser",
        "email": registered_user['email'],
        "first_name": "Test",
        "last_name": "User",
        "password": "password"
    }
    response = client.post('/user/register', json=payload)
    assert response.status_code == 409
    
def test_user_registration_missing_required_fields(client):
    payload = {
        "email": "test@example.com",
        "last_name": "User",
        "password": "password123"
    }

    response = client.post('/user/register', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "errors" in data

    errors = data["errors"]
    assert errors["username"][0] == "Missing data for required field."
    assert errors["first_name"][0] == "Missing data for required field."
    
    
def test_login_with_email(client, registered_user):
    payload = {
       "email":registered_user['email'],
        "password": registered_user['password']
    }
    
    response = client.post('/user/login', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'refresh_token' in data
    
def test_login_wrong_password(client, registered_user):
    payload = {
        "email": registered_user['email'],
        "password": "wrongpassword"
    }
    response = client.post('/user/login', json=payload)

    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid credentials"