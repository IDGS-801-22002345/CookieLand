from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# Importar rutas correctamente desde el módulo 'routes'
from config import DevelopmentConfig
from models.proveedor_model import db
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.proveedor_routes import provedor_bp

# Protección contra CSRF
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    csrf.init_app(app)
   
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()

    # Rutas importadas
    app.register_blueprint(cliente_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(provedor_bp)

    return app  # Asegúrate de devolver la instancia de la app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)  # Ahora puede llamar a app.run() correctamente
