from flask import Flask, current_app, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

from config import DevelopmentConfig
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.personal_routes import personal_bp
from routes.registro_compras_routes import registro_compras_bp
from routes.inventario_routes import inventario_bp
from models.models import *
from routes.proveedor_routes import provedor_bp
from routes.inventario_routes import inventario_bp
# from models.proveedor_model import db
# from models.materia_prima_model import db
app = Flask(__name__)

# Protección contra CSRF
csrf = CSRFProtect()
def create_app():
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        with current_app.app_context():
            return db.session.get(Usuario, int(user_id))
 
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    with app.app_context():
      db.create_all()             
      Role.insertar_roles()      
      Usuario.insertar_admin()   

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(personal_bp)
    app.register_blueprint(registro_compras_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(provedor_bp)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', debug=True)
