import os
from sqlalchemy import create_engine

import urllib

class Config(object):
    SECRET_KEY='Clave nueva'
    SESSION_COOCKE_SECRET=False

class DevelopmentConfig(Config):
    DEBUG= True
    SQLALCHEMY_DATABASE_URI= "mysql+pymysql://root:1998@127.0.0.1/maicookies"
    SQLALCHEMY_TRACK_MODIFICATIONS=False