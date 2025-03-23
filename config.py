import os
from datetime import timedelta

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave_super_secreta"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5) 

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:admin@localhost/dongalleto"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


