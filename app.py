from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# Importar rutas correctamente desde el modulo 'routes'
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp
from routes.personal_routes import personal_bp
from routes.registro_compras_routes import registro_compras_bp
from routes.inventario_routes import inventario_bp

app = Flask(__name__)

# Protección contra CSRF
csrf = CSRFProtect()

# Rutas importadas
app.register_blueprint(cliente_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(personal_bp)
app.register_blueprint(registro_compras_bp)
app.register_blueprint(inventario_bp)

if __name__ == '__main__':
    csrf.init_app(app)
    app.run(debug=True)
