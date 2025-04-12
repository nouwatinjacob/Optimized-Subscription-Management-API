from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import config


def create_app(confi_name):
    app = Flask(__name__)
    app.config.from_object(config[confi_name])
    db = SQLAlchemy()
    db.init_app(app)

    return app