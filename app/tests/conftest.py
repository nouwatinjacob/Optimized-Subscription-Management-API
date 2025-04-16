import pytest
from flask_jwt_extended import create_access_token
from app import create_app
from app.config import config
from app.extensions import db
from app.models.user import User
from app.models.plan import Plan
import uuid

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.from_object(config['test'])

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

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

@pytest.fixture
def user_and_token(app):
    with app.app_context():
        unique_str = uuid.uuid4().hex[:6]
        user = User(
            email=f"test{unique_str}@example.com",
            username=f"testuser_{unique_str}",
            first_name="Test",
            last_name="User",
            password="password"
        )
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
        return user, token

@pytest.fixture
def plan(app):
    with app.app_context():
        plan = Plan(name="Basic-" + str(uuid.uuid4()), price=10.0)
        db.session.add(plan)
        db.session.commit()
        db.session.refresh(plan)
        return plan