import os
from flask import Flask
from .config import config
from .extensions import db, jwt, migrate
from .routes.user import user_bp
from .routes.plan import plan_bp
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
    
    # register Blueprints
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(plan_bp, url_prefix='/plan')
    

    return app