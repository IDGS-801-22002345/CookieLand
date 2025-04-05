from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima, Produccion
from forms.merma_forms import MermaForm
import traceback 
import datetime
from utils.decoradores import *

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/mk_merma')

@merma_bp.route("/")
def index():
    create_form = MermaForm(request.form)
    
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    producciones = Produccion.query.all()
    create_form.produccion_id.choices = [(p.id, p.galleta.nombre) for p in producciones]
    
    mermas = Merma.query.all()
    
    return render_template("merma/merma.html", form=create_form, mermas=mermas)

@merma_bp.route("/crear", methods=['POST'])
@registrar_accion("Agrego merma")
@login_required
@log_excepciones
@role_required('admin')
def crear():  
    create_form = MermaForm(request.form)
    
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    producciones = Produccion.query.all()
    create_form.produccion_id.choices = [(p.id, p.galleta.nombre) for p in producciones]

    if create_form.validate():
        tipo_merma = create_form.tipo_merma.data
        cantidad = create_form.cantidad.data
        inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
        produccion_id = create_form.produccion_id.data if tipo_merma == 'galleta' else None

        inventario_item = None
        item_nombre = None

        if produccion_id:
            produccion = Produccion.query.get(produccion_id)
            if not produccion:
                flash('Error: Producción no encontrada.', 'danger')
                return redirect(url_for('merma_bp.index'))
            inventario_item = produccion
            item_nombre = produccion.galleta.nombre if produccion.galleta else "Galleta desconocida"

        if inventario_materia_id:
            inventario_materia = InventarioMateria.query.get(inventario_materia_id)
            if not inventario_materia:
                flash('Error: Inventario de insumos no encontrado.', 'danger')
                return redirect(url_for('merma_bp.index'))
            inventario_item = inventario_materia
            item_nombre = inventario_materia.materia_prima.nombre if inventario_materia.materia_prima else "Insumo desconocido"

        if inventario_item:
            cantidad_actual = inventario_item.cantidad if hasattr(inventario_item, 'cantidad') else inventario_item.stock
            
            if cantidad_actual < cantidad:
                flash(f'Error: No hay suficiente stock de {item_nombre}. Stock actual: {cantidad_actual}', 'danger')
                return redirect(url_for('merma_bp.index'))
            
            if hasattr(inventario_item, 'cantidad'):
                inventario_item.cantidad -= cantidad
                
                if inventario_item.cantidad <= 0:
                    inventario_item.estado_stock = 'agotado'
                    flash(f'¡ALERTA! El stock de {item_nombre} se ha agotado completamente.', 'danger')
                elif inventario_item.cantidad < inventario_item.cantidad_minima:
                    inventario_item.estado_stock = 'bajo'
                    flash(f'¡Advertencia! Stock bajo de {item_nombre}. Quedan {inventario_item.cantidad} unidades.', 'warning')
                else:
                    inventario_item.estado_stock = 'normal'
                    flash(f'Stock actual de {item_nombre}: {inventario_item.cantidad} unidades', 'info')
            else:
                inventario_item.stock -= cantidad

            merma = Merma(
                descripcion=create_form.descripcion.data,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                inventario_materia_id=inventario_materia_id,
                produccion_id=produccion_id
            )
            db.session.add(merma)
            db.session.commit()
            flash(f'Merma registrada correctamente', 'success')

    return redirect(url_for('merma_bp.index'))