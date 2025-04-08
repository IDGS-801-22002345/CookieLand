from flask import Blueprint, render_template
from utils.decoradores import *
from datetime import date
from models.models import Galleta, Compra, Venta, db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/mk_dashboard')

def obtener_total_ventas_dia():
    hoy = date.today()
    ventas = Venta.query.filter(db.func.date(Venta.fechaCreacion) == hoy).all()
    return sum(v.total for v in ventas)

def obtener_total_compras_dia():
    hoy = date.today()
    compras = Compra.query.filter(db.func.date(Compra.create_date) == hoy).all()
    return sum(c.total for c in compras)

def calcular_total_caja(fondo_inicial, total_ventas, total_compras):
    return fondo_inicial + total_ventas - total_compras


@dashboard_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    top_5_galletas = db.session.query(
    Galleta.id, 
    Galleta.nombre, 
    Galleta.precio, 
    func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Galleta.id).order_by(func.sum(DetalleVenta.cantidad).desc()).limit(5).all()

    # ⚠️ Inventario bajo (por ahora simulado)
    inventario_critico = db.session.query(InventarioMateria).join(MateriaPrima).filter(
        InventarioMateria.cantidad < InventarioMateria.cantidad_minima
    ).all()

    # 📦 Pedidos para hoy (por ahora simulados)
    pedidos_hoy = [
        {"cliente_nombre": "Juan Pérez", "producto": "Caja de Galletas de Chocolate", "fecha_entrega": "2025-04-05"},
        {"cliente_nombre": "María López", "producto": "Caja de Galletas de Vainilla", "fecha_entrega": "2025-04-05"}
    ]

    # 💵 Métricas reales del día
    fondo_inicial = 1500
    ventas_dia = obtener_total_ventas_dia()
    compras_dia = obtener_total_compras_dia()
    total_caja = calcular_total_caja(fondo_inicial, ventas_dia, compras_dia)

    return render_template(
        "dashboard/dashboard.html",
        ventas_dia=ventas_dia,
        compras_dia=compras_dia,
        fondo_inicial=fondo_inicial,
        total_caja=total_caja,
        top_5_galletas=top_5_galletas,
        inventario_critico=inventario_critico,
        pedidos_hoy=pedidos_hoy,
        galletas_producidas_hoy=300  # <- lo puedes automatizar después también
    )
