from flask import Blueprint, render_template, session
from utils.decoradores import *

cliente_bp = Blueprint('cliente_bp', __name__, url_prefix='/')

# Ruta de layout
@cliente_bp.route('/layout')
@log_excepciones
@login_required
def layout():
    return render_template('cliente/layout.html')

@cliente_bp.route('/')
@log_excepciones
def index():
 # Verificar si el usuario está autenticado
    if 'user_id' in session:
        username = session['username']
        email = session['email']
        return render_template('cliente/index.html', username=username, correo=email)
    else:
        return render_template('cliente/index.html')
    
# Ruta de nosotros
@cliente_bp.route('/nosotros')
@log_excepciones
def nosotros():
    return render_template('cliente/nosotros.html')

# Ruta de la galeria de calletas
@cliente_bp.route('/galeria')
@log_excepciones
def geleria():
    return render_template('cliente/galeria.html')

# Ruta de contacto
@cliente_bp.route('/contacto')
@log_excepciones
def contacto():
    return render_template('cliente/contacto.html')

# Ruta de aviso de privacidad
@cliente_bp.route('/aviso-de-privacidad')
@log_excepciones
def avisodeprivacidad():
    return render_template('cliente/avisodeprivacidad.html')

# Ruta de terminos y condiciones
@cliente_bp.route('/terminos-y-condiciones')
@log_excepciones
def terminosycondiciones():
    return render_template('cliente/terminosycondiciones.html')

# Ruta de productos
@cliente_bp.route('/productos')
@log_excepciones
def productos():
    return render_template('cliente/productos.html')

# Ruta de carrito productos
@cliente_bp.route('/carrito_compras')
@log_excepciones
def carrito_compras():
    return render_template('cliente/carrito_compras.html')






