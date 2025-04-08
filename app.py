import os
from flask import Flask, current_app, flash, render_template, request, redirect, session, url_for
from flask_wtf.csrf import CSRFProtect
import base64
from flask_login import LoginManager, current_user 
from config import *
from models.models import *
from flask_mail import Mail
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Rutas importadas
from routes.auth_routes import auth_bp
from routes.cliente_routes import cliente_bp
from routes.detalle_compras import detalle_compras_bp
from routes.registro_compras_routes import registro_compras_bp
from routes.inventario_routes import inventario_bp
from routes.galletas_routes import galletas_bp
from routes.dashboard_routes import dashboard_bp
from routes.materia_prima_routes import materia_prima_bp
from routes.merma_routes import merma_bp
from routes.personal_routes import personal_bp
from routes.produccion_routes import produccion_bp
from routes.proveedor_routes import provedor_bp
from routes.venta_routes import ventas_bp
from routes.ventaDetalle_routes import ventasDetalles_bp


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


    # Rutas importadas
    app.register_blueprint(cliente_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(personal_bp)
    app.register_blueprint(registro_compras_bp)
    app.register_blueprint(materia_prima_bp)
    app.register_blueprint(provedor_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(detalle_compras_bp)
    app.register_blueprint(merma_bp)
    app.register_blueprint(galletas_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(ventasDetalles_bp)
    app.register_blueprint(dashboard_bp)


    app.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8') if x else None


    # Configuración de archivos logs
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    if not os.path.exists('logs'):
        os.mkdir('logs')

    log_filename = f'logs/app_{datetime.today().strftime("%Y-%m-%d")}.log'

    file_handler = TimedRotatingFileHandler(
        log_filename,
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
    
    @app.before_request
    def cargar_carrito_temporal():
        if current_user.is_authenticated and 'carrito' not in session:
            carrito = {}
            items = CarritoTemporal.query.filter_by(usuario_id=current_user.id).all()
            for item in items:
                carrito[str(item.galleta_id)] = {'cantidad': item.cantidad}
            session['carrito'] = carrito  
    
    @app.route('/limpiar-carrito')
    def limpiar_carrito():
        session.pop('carrito', None)
        flash("Carrito limpiado.", "info")
        return redirect(url_for('cliente_bp.productos'))  
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
