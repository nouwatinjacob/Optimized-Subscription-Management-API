from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User

def authenticate_user(email, password):
    """Authenticate user by email and return an access token and refresh token"""
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return user, None, 200
    
    return None, "Invalid credentials", 400
