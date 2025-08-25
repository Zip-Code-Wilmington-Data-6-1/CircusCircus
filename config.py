"""
Flask configuration variables.
"""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Set Flask configuration from .env file."""
    # General Config
    SECRET_KEY = environ.get('SECRET_KEY', 'dev_default_secret')
    FLASK_APP = environ.get('FLASK_APP', 'forum.app')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL', 'sqlite:///circuscircus.db')
    SQLALCHEMY_ECHO = environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False