from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# Importar rutas correctamente desde el módulo 'routes'
from config import DevelopmentConfig
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.personal_routes import personal_bp
from routes.registro_compras_routes import registro_compras_bp
from routes.inventario_routes import inventario_bp
from models.db import db
from routes.proveedor_routes import provedor_bp
from routes.galletas_routes import recetas_bp
# from models.proveedor_model import db
# from models.materia_prima_model import db



app = Flask(__name__)

# Protección contra CSRF
csrf = CSRFProtect()
def create_app():
 
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        db.create_all()
    return app     
# Rutas importadas
app.register_blueprint(cliente_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(personal_bp)
app.register_blueprint(registro_compras_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(provedor_bp)
app.register_blueprint(recetas_bp)


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
