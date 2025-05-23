import os
from flask.cli import load_dotenv
import json
import os
from datetime import timedelta


load_dotenv() 

class Config(object):
    SECRET_KEY = 'Clave Nueva'
    SESSION_COOKIE_SECURE = False
    
    DEBUG = False  
    TESTING = False
    PROPAGATE_EXCEPTIONS = False 
    EXPLAIN_TEMPLATE_LOADING = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    
    # Tiempo de la sesion activaaa
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_REFRESH_EACH_REQUEST = True

