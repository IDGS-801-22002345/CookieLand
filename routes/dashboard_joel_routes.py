from sqlite3 import IntegrityError
from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash
from models.models import Receta, Galleta, MateriaPrima, DetalleReceta, Produccion
from forms.galletas_forms import GalletasForm, InsumosForm, GalletasEditForm
from models.models import db
from utils.decoradores import *
from datetime import date
from models.models import Compra


dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

from flask import render_template
from models.models import Galleta  # Asegúrate de importar el modelo Galleta

@dashboard_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    # Obtenemos las 5 galletas más vendidas (simuladas)
    top_5_galletas = [
        {"id": 1, "nombre": "Galleta de Chocolate", "total_vendido": 120},
        {"id": 2, "nombre": "Galleta de Vainilla", "total_vendido": 95},
        {"id": 3, "nombre": "Galleta de Avena", "total_vendido": 85},
        {"id": 4, "nombre": "Galleta de Limón", "total_vendido": 75},
        {"id": 5, "nombre": "Galleta de Fresa", "total_vendido": 60}
    ]

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

    # Galletas producidas hoy (simuladas)
    galletas_producidas_hoy = 300

    # Métricas del día (simuladas)
    ventas_dia = 1000  # Reemplazar con el valor real
    compras_dia = 500  # Reemplazar con el valor real
    fondo_inicial = 1500  # Reemplazar con el valor real
    total_caja = 2500  # Reemplazar con el valor real

    return render_template(
        "dashboard_joel/dashboard.html",
        ventas_dia=ventas_dia,
        compras_dia=compras_dia,
        fondo_inicial=fondo_inicial,
        total_caja=total_caja,
        top_5_galletas=top_5_galletas,
        inventario_critico=inventario_critico,
        pedidos_hoy=pedidos_hoy,
        galletas_producidas_hoy=galletas_producidas_hoy
    )