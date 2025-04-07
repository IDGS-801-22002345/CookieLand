from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
from models.models import Galleta, db, Venta, DetalleVenta
from forms.venta_forms import VentaForm
from utils.decoradores import login_required, log_excepciones, role_required

ventasDetalles_bp = Blueprint('ventasDetalles_bp', __name__, url_prefix='/ventas-detalles')


@ventasDetalles_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    ventas = Venta.query.options(
        db.joinedload(Venta.detalles).joinedload(DetalleVenta.galleta),
        db.joinedload(Venta.usuario)
    ).order_by(Venta.fechaCreacion.desc()).all()
    
    return render_template(
        "venta/detalleVenta.html", 
        ventas=ventas
    )
# @ventas_bp.route('/imagen/<int:galleta_id>')
# def mostrar_imagen(galleta_id):
#     galleta = Galleta.query.get_or_404(galleta_id)
#     if not galleta.foto:
#         return send_from_directory('static', 'images/default-cookie.png')
#     return Response(galleta.foto, mimetype='image/jpeg')



    