from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.models import MateriaPrima, InventarioMateria, db
from routes.auth_routes import role_required 
from utils.decoradores import *
 

inventario_bp = Blueprint('inventario_bp', __name__, url_prefix='/')

@inventario_bp.route('/inventario', methods=['GET', 'POST'])
@log_excepciones
@login_required
@role_required('admin')
def index():
    inventario = db.session.query(MateriaPrima).outerjoin(InventarioMateria).all()
    return render_template('inventario/inventario.html', inventario=inventario)