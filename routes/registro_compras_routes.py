from flask import Blueprint, render_template

registro_compras_bp = Blueprint('registro_compras_bp', __name__, url_prefix='/')

@registro_compras_bp.route('/registro-compras')
def compras():
    return render_template('compras/registro_compras.html')
