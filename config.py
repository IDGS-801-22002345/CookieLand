import os
from sqlalchemy import create_engine

import urllib

class Config(object):
    SECRET_KEY = 'Clave Nueva'
    SESSION_COOKIE_SECURE = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Deadmau6@localhost/bdidgs801'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    RECAPTCHA_PUBLIC_KEY = '6LemBAIrAAAAAL69KGKIprR-Z577orMrDPVX94f1'
    RECAPTCHA_PRIVATE_KEY = '6LemBAIrAAAAALTrVi0_ILffDwwozOYvb5pzZKO9'
    