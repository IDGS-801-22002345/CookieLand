from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from forms.materia_prima_form import MateriaPrimaForm
from models.models import MateriaPrima, InventarioMateria, db

materia_prima_bp = Blueprint('materia_prima_bp', __name__, url_prefix='/')


@materia_prima_bp.route('/materia-prima', methods=['GET', 'POST'])
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


@materia_prima_bp.route("/agregar", methods=['POST'])
def agregar():
    create_form = MateriaPrimaForm(request.form)
    if request.method == "POST":
        # Crear la materia prima
        nueva_materia = MateriaPrima(
            nombre=create_form.nombre.data,
            unidad=create_form.unidad.data
        )
        db.session.add(nueva_materia)
        db.session.commit()

        flash("Materia Prima agregada con éxito", "success")
    else:
        flash("Error al agregar la materia prima", "error")
    
    return redirect(url_for('materia_prima_bp.index'))


@materia_prima_bp.route('/modificar', methods=["GET", "POST"])
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