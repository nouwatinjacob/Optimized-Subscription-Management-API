import pytest
from app import create_app
from app.config import config
from app.extensions import db
from app.models.user import User

            
@pytest.fixture
def client():
    app = create_app()
    app.config.from_object(config['test'])

    with app.app_context():
        db.create_all() 

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()

     
@pytest.fixture
def registered_user(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password"
    }
    client.post('/user/register', json=payload)
    return payload