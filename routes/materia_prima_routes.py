from sqlite3 import IntegrityError
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from forms.materia_prima_form import MateriaPrimaForm
from models.models import MateriaPrima, InventarioMateria, db
from utils.decoradores import *

materia_prima_bp = Blueprint('materia_prima_bp', __name__, url_prefix='/')


@materia_prima_bp.route('/mk_materia-prima', methods=['GET', 'POST'])
@login_required
@log_excepciones
@role_required('admin')
def index():
    create_form = MateriaPrimaForm(request.form)
    # Consulta que une materia_prima con inventario_materia
    materia_prima = (
        MateriaPrima.query
        .outerjoin(InventarioMateria)
        .order_by(MateriaPrima.nombre.asc())
        .all()
    )
    return render_template('materia_prima/materia_prima.html', form=create_form, materia_prima=materia_prima)


@materia_prima_bp.route("/mk_agregar", methods=['POST'])
@registrar_accion("Agrego materia prima")
@login_required
@log_excepciones
@role_required('admin')
def agregar():
    create_form = MateriaPrimaForm(request.form)
    
    if request.method == "POST":
        try:
            # Crear la materia prima
            nueva_materia = MateriaPrima(
                nombre=create_form.nombre.data,
                unidad=create_form.unidad.data
            )
            
            # Agregar la materia prima primero
            db.session.add(nueva_materia)
            db.session.commit()  # Commit para obtener el id generado automáticamente
            
            # Establecer la cantidad mínima dependiendo de la unidad
            if nueva_materia.unidad in ['gramos', 'g']:
                cantidad_minima = 1000
            elif nueva_materia.unidad in ['mililitros', 'ml']:
                cantidad_minima = 1000
            elif nueva_materia.unidad in ['piezas', 'pz']:
                cantidad_minima = 30
            else:
                cantidad_minima = 0  # Si no es ninguna de las anteriores, se puede manejar de forma predeterminada
            
            # Crear el inventario con la cantidad mínima
            nuevo_inventario = InventarioMateria(
                cantidad=0,
                cantidad_minima=cantidad_minima,
                estado_stock='Sin Stock',
                material_id=nueva_materia.id  # Ahora se asigna el ID generado
            )
            
            # Agregar el inventario
            db.session.add(nuevo_inventario)
            db.session.commit()

            flash("Materia Prima agregada con éxito", "success")
        
        except IntegrityError:
            db.session.rollback() 
            flash("Error: El insumo ya existe. Por favor, elige otro.", "danger")
    
    return redirect(url_for('materia_prima_bp.index'))




@materia_prima_bp.route('/mk_modificar', methods=["GET", "POST"])
@registrar_accion("Modifico materia prima")
@login_required
@log_excepciones
@role_required('admin')
def modificar():
    create_form = MateriaPrimaForm(request.form)
    
    if request.method == "GET":
        id = request.args.get('id')
        materia_prima = db.session.query(MateriaPrima).filter(MateriaPrima.id == id).first()
        if materia_prima:
            create_form.id.data = id
            create_form.nombre.data = materia_prima.nombre
            create_form.unidad.data = materia_prima.unidad
        else:
            flash("Materia Prima no encontrada", "error")
            return redirect(url_for('materia_prima_bp.index'))

    elif request.method == "POST":
        id = create_form.id.data
        materia_prima = db.session.query(MateriaPrima).filter(MateriaPrima.id == id).first()
        if materia_prima:
            materia_prima.nombre = create_form.nombre.data
            materia_prima.unidad = create_form.unidad.data
            db.session.commit()
            flash("Materia Prima modificada con éxito", "success")
        else:
            flash("Materia Prima no encontrada", "error")
        return redirect(url_for('materia_prima_bp.index'))

    materia_prima = MateriaPrima.query.all()
    return render_template('materia_prima/materia_prima.html', form=create_form, materias_primas=materia_prima, modificar_modal=True)