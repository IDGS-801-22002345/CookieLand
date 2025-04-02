import os
from dotenv import load_dotenv

load_dotenv()  # Esto carga las variables del archivo .env

class Config(object):
    SECRET_KEY = 'Clave Nueva'
    SESSION_COOKIE_SECURE = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    # Corrección 1: Nombre correcto de la variable de entorno (y quité el typo en TRACK_MODIFICATIONS)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')  # ← ¡Cambiado de DATABASE_URL!
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # ← ¡Corregido el typo (TRACK no TRACK)!
    
    # Corrección 2: Nombre correcto de las variables de entorno (sin typo en PUBLIC)
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')  # ← ¡Corregido PUBLIC_KEY!
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')