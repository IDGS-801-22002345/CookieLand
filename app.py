from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from models.models import db  

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    csrf.init_app(app)
    
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()

    from routes.cliente_routes import cliente_bp
    from routes.auth_routes import auth_bp
    from routes.personal_routes import personal_bp

    app.register_blueprint(cliente_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(personal_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)