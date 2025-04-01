from flask import Flask, current_app
from flask_wtf.csrf import CSRFProtect
import base64
from flask_login import LoginManager
from config import DevelopmentConfig
from models.models import db 
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.personal_routes import personal_bp
from routes.registro_compras_routes import registro_compras_bp
from routes.proveedor_routes import provedor_bp
from routes.galletas_routes import recetas_bp
from routes.inventario_routes import inventario_bp
from routes.materia_prima_routes import materia_prima_bp
from routes.merma_routes import merma_bp

def create_app():
    app = Flask(__name__)
    
    # Configuración esencial
    app.config.from_object(DevelopmentConfig)
    
    # Inicialización de extensiones
    db.init_app(app)
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)
    
    # Configuración de LoginManager
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return db.session.get(Usuario, int(user_id))
    
    # Creación de tablas
    with app.app_context():
        db.create_all()
    
    # Registro de blueprints
    blueprints = [
        cliente_bp,
        auth_bp,
        personal_bp,
        registro_compras_bp,
        materia_prima_bp,
        provedor_bp,
        inventario_bp,
        recetas_bp,
        merma_bp
    ]
    
    for bp in blueprints:
        app.register_blueprint(bp)
    
    app.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8') if x else None
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)