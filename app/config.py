import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'super-secret-key'
    DEBUG = False
    
    

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    

config = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
)