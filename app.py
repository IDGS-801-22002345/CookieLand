from dotenv import load_dotenv
import os
from flask import Flask, current_app, render_template, request, redirect, session, url_for
from flask_wtf.csrf import CSRFProtect
import base64
from flask_login import LoginManager
from config import *
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.personal_routes import personal_bp
from routes.registro_compras_routes import registro_compras_bp
from models.models import *
from routes.proveedor_routes import provedor_bp
from routes.galletas_routes import galletas_bp
from routes.inventario_routes import inventario_bp
from routes.materia_prima_routes import materia_prima_bp
from flask_mail import Mail
import logging
from logging.handlers import TimedRotatingFileHandler
from routes.produccion_routes import produccion_bp
from routes.detalle_compras import detalle_compras_bp



app = Flask(__name__)

csrf = CSRFProtect()
mail = Mail()  


def create_app():
    
    @app.errorhandler(404)
    def error_interno(error):
        app.logger.error(f"Error 404: {request.url} - {str(error)}")
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def error_interno(error):
        app.logger.error(f"Error 500: {request.url} - {str(error)}")
        return render_template("500.html"), 500

        
    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    login_manager.login_message = 'Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        with current_app.app_context():
            return db.session.get(Usuario, int(user_id))
 
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        db.create_all()
        Role.insertar_roles()
        Usuario.insertar_admin()

    # Rutas importadas
    app.register_blueprint(cliente_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(personal_bp)
    app.register_blueprint(registro_compras_bp)
    app.register_blueprint(materia_prima_bp)
    app.register_blueprint(provedor_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(galletas_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(detalle_compras_bp)


    app.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8') if x else None


    # Configurcion de archivos logs
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = TimedRotatingFileHandler(
        'logs/app.log',
        when='midnight',         
        interval=1,
        backupCount=7,         
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    
    # Cabecera de seguridad 
    @app.after_request
    def aplicar_cabeceras_seguridad(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app


app.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8') if x else None

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)