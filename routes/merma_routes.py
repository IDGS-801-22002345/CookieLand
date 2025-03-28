from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima
from forms.merma_forms import MermaForm

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/merma')

@merma_bp.route("/")
def index():
    create_form = MermaForm(request.form)
    
    # Obtener materias primas con sus nombres
    materias = db.session.query(
        InventarioMateria.id,
        MateriaPrima.nombre
    ).join(MateriaPrima).all()
    
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    # Obtener galletas
    galletas = Galleta.query.all()
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]

    mermas = Merma.query.all()
    return render_template("merma/merma.html", form=create_form, mermas=mermas)

@merma_bp.route("/crear", methods=['POST'])
def crear():
    create_form = MermaForm(request.form)
    
    if create_form.validate():
        merma = Merma(
            descripcion=create_form.descripcion.data,
            cantidad=create_form.cantidad.data,
            tipo_merma=create_form.tipo_merma.data,
            inventario_materia_id=create_form.inventario_materia_id.data,
            inventario_galletas_id=create_form.inventario_galletas_id.data
        )
        db.session.add(merma)
        db.session.commit()
        flash('Merma creada correctamente', 'success')
    else:
        flash('Error al crear la merma', 'danger')
    
    return redirect(url_for('merma_bp.index'))

@merma_bp.route("/modificar/<int:id>", methods=['POST'])
def modificar(id):
    merma = Merma.query.get(id)
    if not merma:
        flash("Merma no encontrada", "error")
        return redirect(url_for('merma_bp.index'))

    create_form = MermaForm(request.form)
    
    if create_form.validate():
        merma.descripcion = create_form.descripcion.data
        merma.cantidad = create_form.cantidad.data
        merma.tipo_merma = create_form.tipo_merma.data
        merma.inventario_materia_id = create_form.inventario_materia_id.data
        merma.inventario_galletas_id = create_form.inventario_galletas_id.data
        
        db.session.commit()
        flash('Merma modificada correctamente', 'success')
    else:
        flash('Error al modificar la merma', 'danger')
    
    return redirect(url_for('merma_bp.index'))