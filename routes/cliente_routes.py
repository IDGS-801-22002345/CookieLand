from flask import Blueprint, render_template

cliente_bp = Blueprint('cliente_bp', __name__, url_prefix='/')

@cliente_bp.route('/')
def index():
    return render_template('cliente/index.html')

@cliente_bp.route('/nosotros')
def nosotros():
    return render_template('cliente/nosotros.html')

@cliente_bp.route('/galeria')
def geleria():
    return render_template('cliente/galeria.html')

@cliente_bp.route('/contacto')
def contacto():
    return render_template('cliente/contacto.html')

@cliente_bp.route('/aviso-de-privacidad')
def avisodeprivacidad():
    return render_template('cliente/avisodeprivacidad.html')

@cliente_bp.route('/terminos-y-condiciones')
def terminosycondiciones():
    return render_template('cliente/terminosycondiciones.html')






