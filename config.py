import os
from sqlalchemy import create_engine

import urllib

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave_super_secreta"
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root1234@127.0.0.1/flaskDB"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

