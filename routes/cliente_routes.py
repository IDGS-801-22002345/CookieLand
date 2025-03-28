from flask import Blueprint, render_template, session

cliente_bp = Blueprint('cliente_bp', __name__, url_prefix='/')

# Ruta de layout
@cliente_bp.route('/layout')
def layout():
    return render_template('cliente/layout.html')

@cliente_bp.route('/')
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
def nosotros():
    return render_template('cliente/nosotros.html')

# Ruta de la galeria de calletas
@cliente_bp.route('/galeria')
def geleria():
    return render_template('cliente/galeria.html')

# Ruta de contacto
@cliente_bp.route('/contacto')
def contacto():
    return render_template('cliente/contacto.html')

# Ruta de aviso de privacidad
@cliente_bp.route('/aviso-de-privacidad')
def avisodeprivacidad():
    return render_template('cliente/avisodeprivacidad.html')

# Ruta de terminos y condiciones
@cliente_bp.route('/terminos-y-condiciones')
def terminosycondiciones():
    return render_template('cliente/terminosycondiciones.html')

# Ruta de productos
@cliente_bp.route('/productos')
def productos():
    return render_template('cliente/productos.html')

# Ruta de carrito productos
@cliente_bp.route('/carrito_compras')
def carrito_compras():
    return render_template('cliente/carrito_compras.html')







