from sqlalchemy import or_
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

def create_user(data):
    """Create a new user and save to the database"""
    if User.query.filter(or_(User.email == data['email'], User.username == data['username'])).first():
        return None, "User already exists", 409

    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    
    return user, None, 201

