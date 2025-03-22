from flask import Blueprint, render_template

inventario_bp = Blueprint('inventario_bp', __name__, url_prefix='/')

@inventario_bp.route('/inventario', methods=['GET', 'POST'])
def compras():
    return render_template('inventario/inventario.html')
