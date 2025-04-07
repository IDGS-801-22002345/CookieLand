from flask import Blueprint, render_template
from utils.decoradores import *
from flask import render_template
from models.models import Galleta, Compra


dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    # Obtenemos las primeras 5 galletas (reales, no simuladas)
    top_5_galletas = Galleta.query.limit(5).all()
    print(top_5_galletas)

    # Datos simulados de inventario bajo
    inventario_critico = [
        {"nombre": "Harina", "cantidad_restante": 800},
        {"nombre": "Azúcar", "cantidad_restante": 500},
        {"nombre": "Mantequilla", "cantidad_restante": 200},
    ]

    # Pedidos para hoy (simulados)
    pedidos_hoy = [
        {"cliente_nombre": "Juan Pérez", "producto": "Caja de Galletas de Chocolate", "fecha_entrega": "2025-04-05"},
        {"cliente_nombre": "María López", "producto": "Caja de Galletas de Vainilla", "fecha_entrega": "2025-04-05"}
    ]

    # Métricas del día (simuladas)
    ventas_dia = 1000
    compras_dia = 500
    fondo_inicial = 1500
    total_caja = 2500

    return render_template(
        "dashboard/dashboard.html",
        ventas_dia=ventas_dia,
        compras_dia=compras_dia,
        fondo_inicial=fondo_inicial,
        total_caja=total_caja,
        top_5_galletas=top_5_galletas,
        inventario_critico=inventario_critico,
        pedidos_hoy=pedidos_hoy,
        galletas_producidas_hoy=300
    )