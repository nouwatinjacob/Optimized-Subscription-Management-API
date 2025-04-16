from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.schemas.user import UserRegisterSchema, UserLoginSchema
from flask_jwt_extended import create_access_token, create_refresh_token
from app.services.user import create_user
from app.services.auth import authenticate_user

user_bp = Blueprint('user', __name__)
register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@user_bp.post('/register')
def register_user():
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    user, error, status = create_user(data)

    if error:
        return jsonify({"error": error}), status
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "User created successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), status
    
@user_bp.post('/login')
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    user, error, status = authenticate_user(data['email'], data['password'])

    if error:
        return jsonify({"error": error}), status

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), status