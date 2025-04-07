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
    ventaForm = VentaForm()
    ventas = Venta.query.options(
        db.joinedload(Venta.detalles).joinedload(DetalleVenta.galleta),
        db.joinedload(Venta.usuario)
    ).order_by(Venta.fechaCreacion.desc()).all()
    
    return render_template(
        "venta/detalleVenta.html", 
        modal=False, 
        form=ventaForm,
        ventas=ventas
    )


@ventasDetalles_bp.route("/abrirmodal", methods=["POST"])
def abrir_modal():
     ventaForm = VentaForm()
     venta_id = int(request.form.get('venta_id'))
     print('Entro')
     print(venta_id)
     venta = Venta.query.options(
        db.joinedload(Venta.detalles).joinedload(DetalleVenta.galleta),
        db.joinedload(Venta.usuario)
     ).get_or_404(venta_id)
     ventas = Venta.query.options(
        db.joinedload(Venta.detalles).joinedload(DetalleVenta.galleta),
        db.joinedload(Venta.usuario)
    ).order_by(Venta.fechaCreacion.desc()).all()
     return render_template(
        "venta/detalleVenta.html", 
        modal=True, 
        form=ventaForm,
        ventas=ventas,
        venta=venta
    )

@ventasDetalles_bp.route("/cerrarmodal", methods=["POST"])
def cerrar_modal():
 return redirect(url_for('ventasDetalles_bp.index'))

# @ventas_bp.route('/imagen/<int:galleta_id>')
# def mostrar_imagen(galleta_id):
#     galleta = Galleta.query.get_or_404(galleta_id)
#     if not galleta.foto:
#         return send_from_directory('static', 'images/default-cookie.png')
#     return Response(galleta.foto, mimetype='image/jpeg')



    