from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# Importar rutas correctamente desde el módulo 'routes'
from routes.cliente_routes import cliente_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)

# Protección contra CSRF
csrf = CSRFProtect()

# Rutas importadas
app.register_blueprint(cliente_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    csrf.init_app(app)
    app.run(debug=True)
