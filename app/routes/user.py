from flask import request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from app.schemas.user import UserRegisterSchema, UserLoginSchema
from flask_jwt_extended import create_access_token, create_refresh_token
from app.services.user import create_user
from app.services.auth import authenticate_user


user_ns = Namespace('user', description='User operations')
register_model = user_ns.model('RegisterUser', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'password': fields.String(required=True),
})

login_model = user_ns.model('LoginUser', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

# user_bp = Blueprint('user', __name__)
register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@user_ns.route('/register')
class Register(Resource):
    """
    Registers a new user and returns access and refresh tokens.
    Validates the registration data, creates the user, and issues tokens.
    """
    @user_ns.expect(register_model)
    @user_ns.response(201, "User created successfully")
    @user_ns.response(400, "Validation Error")
    def post(self):
        data = request.get_json()
        try:
            validated = register_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        user, error, status = create_user(validated)

        if error:
            return {"error": error}, status
        
        return {
        "message": "User created successfully",
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id))
    }, status


@user_ns.route('/login')
class Login(Resource):
    """
    Authenticates a user and returns access and refresh tokens.
    Validates login data, performs authentication, and issues tokens.
    """
    @user_ns.expect(login_model)
    @user_ns.response(200, "Login successful")
    @user_ns.response(400, "Validation Error")
    def post(self):
        data = request.get_json()
        try:
            validated = login_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        user, error, status = authenticate_user(validated["email"], validated["password"])

        if error:
            return {"error": error}, status
        
        return {
            "access_token": create_access_token(identity=user.id),
            "refresh_token": create_refresh_token(identity=user.id),
        }, status
