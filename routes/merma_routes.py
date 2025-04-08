from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima, Produccion
from forms.merma_forms import MermaForm
import traceback 
import datetime
from utils.decoradores import *

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/mk_merma')

@merma_bp.route("/")
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
def index():
    create_form = MermaForm(request.form)

    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]

    galletas = Galleta.query.all()
    create_form.galleta_id.choices = [(g.id, g.nombre) for g in galletas]

    mermas = Merma.query.all()

    return render_template("merma/merma.html", form=create_form, mermas=mermas)


@merma_bp.route("/crear", methods=['POST'])
@registrar_accion("Agrego merma")
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
def crear():
    create_form = MermaForm(request.form)

    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]

    galletas = Galleta.query.all()
    create_form.galleta_id.choices = [(g.id, g.nombre) for g in galletas]

    if create_form.validate():
        tipo_merma = create_form.tipo_merma.data
        cantidad = create_form.cantidad.data
        inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
        galleta_id = create_form.galleta_id.data if tipo_merma == 'galleta' else None

        inventario_item = None
        item_nombre = None

        if galleta_id:
            galleta = Galleta.query.get(galleta_id)
            if not galleta:
                flash('Error: Galleta no encontrada.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = galleta
            item_nombre = galleta.nombre

        if inventario_materia_id:
            inventario_materia = InventarioMateria.query.get(inventario_materia_id)
            if not inventario_materia:
                flash('Error: Inventario de insumos no encontrado.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = inventario_materia
            item_nombre = inventario_materia.materia_prima.nombre if inventario_materia.materia_prima else "Insumo desconocido"

        if inventario_item:
            cantidad_actual = inventario_item.cantidad if hasattr(inventario_item, 'cantidad') else getattr(inventario_item, 'stock', 0)

            if cantidad_actual < cantidad:
                flash(f'Error: No hay suficiente stock de {item_nombre}. Stock actual: {cantidad_actual}', 'warning')
                return redirect(url_for('merma_bp.index'))

            if hasattr(inventario_item, 'cantidad'):
                inventario_item.cantidad -= cantidad

                if inventario_item.cantidad == 0:
                    inventario_item.estado_stock = 'Agotado'
                    flash(f'¡ALERTA! El stock de {item_nombre} se ha agotado completamente.', 'warning')
                elif inventario_item.cantidad < inventario_item.cantidad_minima:
                    inventario_item.estado_stock = 'Bajo'
                    flash(f'¡Advertencia! Stock bajo de {item_nombre}. Quedan {inventario_item.cantidad} unidades.', 'warning')
                else:
                    inventario_item.estado_stock = 'Alto' 
                    flash(f'Stock actual de {item_nombre}: {inventario_item.cantidad} unidades', 'info')
            else:
                inventario_item.stock -= cantidad  

            merma = Merma(
                descripcion=create_form.descripcion.data,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                inventario_materia_id=inventario_materia_id,
                galleta_id=galleta_id
            )
            db.session.add(merma)
            db.session.commit()
            flash(f'Merma registrada correctamente', 'success')

    return redirect(url_for('merma_bp.index'))