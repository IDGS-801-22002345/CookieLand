from flask import Blueprint, render_template

personal_bp = Blueprint('personal_bp', __name__, url_prefix='/')

# Ruta para la ventana de ventas
@personal_bp.route('/ventas')
def ventas():
    return render_template('personal/ventas.html')

# Ruta para del layout
@personal_bp.route('/layout')
def layout():
    return render_template('personal/layout.html')