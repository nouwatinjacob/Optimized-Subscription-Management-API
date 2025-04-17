import os
from flask import Flask
from flask_restx import Api
from .config import config
from .extensions import db, jwt, migrate
from .routes.user import user_ns
from .routes.plan import plan_ns
from .routes.subscription import sub_ns
from dotenv import load_dotenv
load_dotenv()


def create_app():
    app = Flask(__name__)
    
    config_name = os.getenv('ENV_CONFIG') or 'dev'
    app.config.from_object(config[config_name])
    
    @app.route('/')
    def index():
        return "Welcome to Optimized Subscription Management API"
    
    db.init_app(app)
    
    migrate.init_app(app, db)
    
    # initialize JWT
    jwt.init_app(app)
    
    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Optimized Subscription API',
        description='API documentation for Subscription Management',
        doc='/docs'
    )
    
    # Register RESTX Namespaces instead of Blueprints
    api.add_namespace(user_ns, path='/user')
    api.add_namespace(plan_ns, path='/plan')
    api.add_namespace(sub_ns, path='/subscription')

    return app