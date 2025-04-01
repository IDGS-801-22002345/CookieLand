from flask import Blueprint, render_template
from utils.decoradores import *

registro_compras_bp = Blueprint('registro_compras_bp', __name__, url_prefix='/')

@registro_compras_bp.route('/registro-compras')
@login_required
def compras():
    return render_template('compras/registro_compras.html')
