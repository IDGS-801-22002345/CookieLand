from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.receta_model import Receta, Galleta, detalle_recetas, db
from models.materia_prima_model import MateriaPrima
from forms.recetas_forms import RecetaForm

recetas_bp = Blueprint('recetas_bp', __name__, url_prefix='/galletas')


@recetas_bp.route('/recetas', methods=['GET'])
def mostrar_recetas():
    form = RecetaForm()
    form.insumos.append_entry()  

    materiales = MateriaPrima.query.all()
    for insumo_form in form.insumos:
        insumo_form.insumo.choices = [(mp.id, mp.nombre) for mp in materiales]

    recetas = Receta.query.all()
    return render_template('galletas/recetas.html', form=form, recetas=recetas, materiales=materiales)

@recetas_bp.route('/agregar_receta', methods=['POST'])
def agregar_receta():
    if request.method == 'POST':
        nombre_receta = request.form.get('nombre')
        insumos_seleccionados = request.form.getlist('insumos_seleccionados[]')
        cantidades_seleccionadas = request.form.getlist('cantidades_seleccionadas[]')

        # Validar que haya al menos un insumo
        if not insumos_seleccionados or not cantidades_seleccionadas:
            flash('Debes agregar al menos un insumo', 'error')
            return redirect(url_for('recetas_bp.mostrar_recetas'))

        try:
            nueva_receta = Receta(nombre=nombre_receta)
            db.session.add(nueva_receta)
            db.session.flush()  

            for insumo_id, cantidad in zip(insumos_seleccionados, cantidades_seleccionadas):
                db.session.execute(detalle_recetas.insert().values(
                    recetaId=nueva_receta.id,
                    insumoId=insumo_id,
                    cantidad=cantidad
                ))

            db.session.commit()
            flash('Receta agregada correctamente', 'success')
            return redirect(url_for('recetas_bp.mostrar_recetas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar la receta: {str(e)}', 'error')
            return redirect(url_for('recetas_bp.mostrar_recetas'))

            
# Ruta para modificar una receta
@recetas_bp.route('/modificar/<int:id>', methods=['POST'])
def modificar(id):
    receta = Receta.query.get_or_404(id)
    form = RecetaForm(obj=receta)

    if form.validate_on_submit():
        try:
            # Actualiza los datos de la receta
            form.populate_obj(receta)
            db.session.commit()
            flash('Receta modificada correctamente', 'success')
            return redirect(url_for('recetas_bp.mostrar_recetas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar la receta: {str(e)}', 'error')

    return render_template('galletas/recetas.html', form=form, receta=receta)