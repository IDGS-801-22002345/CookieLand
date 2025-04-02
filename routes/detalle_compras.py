from flask import Blueprint, render_template
from models.models import Compra

detalle_compras_bp = Blueprint('detalles_compras_bp', __name__, url_prefix='/')

@detalle_compras_bp.route('/detalle-compras', methods=['GET'])
def index():
    # Ordenar las compras por la fecha de creación de más reciente a más antigua
    compras = Compra.query.order_by(Compra.create_date.desc()).all()  
    return render_template('compras/detalle_compras.html', compras=compras)
