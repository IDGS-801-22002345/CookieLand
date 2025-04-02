from sqlite3 import IntegrityError
from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash
from models.models import Produccion, Galleta
from models.models import db


produccion_bp = Blueprint('produccion_bp', __name__, url_prefix='/produccion')


# Pagina de Produccion

@produccion_bp.route("/")
def index():
    producciones = Produccion.query.options(db.joinedload(Produccion.galleta)).all()
    return render_template("produccion/produccion.html", producciones=producciones)

@produccion_bp.route("/produccion-prod")
def prod():
    producciones = Produccion.query.options(db.joinedload(Produccion.galleta)).all()
    return render_template("produccion/produccionProd.html",producciones=producciones)

@produccion_bp.route('/imagen/<int:galleta_id>')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')  

# Pagina para formulario de agregar receta
