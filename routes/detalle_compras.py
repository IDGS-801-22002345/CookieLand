from flask import Blueprint, render_template
from models.models import Compra
from utils.decoradores import *

detalle_compras_bp = Blueprint('detalle_compras_bp', __name__, url_prefix='/detalle-compras')

@detalle_compras_bp.route('/', methods=['GET'])
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
def index():
    # Ordenar las compras por la fecha de creación de más reciente a más antigua
    compras = Compra.query.order_by(Compra.create_date.desc()).all()  
    return render_template('compras/detalle_compras.html', compras=compras)
