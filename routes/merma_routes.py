from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima, InventarioGalletas
from forms.merma_forms import MermaForm
import traceback 

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/mk_merma')

@merma_bp.route("/")
def index():
    create_form = MermaForm(request.form)
    
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    galletas = Galleta.query.all()
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]
    mermas = Merma.query.all()
    
    return render_template("merma/merma.html", form=create_form, mermas=mermas)

@merma_bp.route("/crear", methods=['POST'])
def crear():  
    create_form = MermaForm(request.form)
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    galletas = Galleta.query.all()
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]

    if create_form.validate():

        tipo_merma = create_form.tipo_merma.data
        cantidad = create_form.cantidad.data
        inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
        inventario_galletas_id = create_form.inventario_galletas_id.data if tipo_merma == 'galleta' else None

        inventario_item = None
        item_nombre = None

        if inventario_galletas_id:
            inventario_galletas = InventarioGalletas.query.get(inventario_galletas_id)
            if not inventario_galletas:
                flash('Error: Inventario de galletas no encontrado.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = inventario_galletas
            item_nombre = inventario_galletas.galleta.nombre if inventario_galletas.galleta else "Galleta desconocida"

        if inventario_materia_id:
            inventario_materia = InventarioMateria.query.get(inventario_materia_id)
            if not inventario_materia:
                flash('Error: Inventario de insumos no encontrado.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = inventario_materia
            item_nombre = inventario_materia.materia_prima.nombre if inventario_materia.materia_prima else "Insumo desconocido"

        if inventario_item:
            if inventario_item.cantidad < inventario_item.cantidad_minima:
                flash(f'¡ATENCIÓN! Stock de {item_nombre} ya está bajo: {inventario_item.cantidad} (mínimo {inventario_item.cantidad_minima})', 'warning')
            
            nuevo_stock = inventario_item.cantidad - cantidad
            if nuevo_stock < inventario_item.cantidad_minima:
               
             merma = Merma(
            descripcion=create_form.descripcion.data,
            cantidad=cantidad,
            tipo_merma=tipo_merma,
            inventario_materia_id=inventario_materia_id,
            inventario_galletas_id=inventario_galletas_id
        )
        db.session.add(merma)

        if tipo_merma == 'insumo' and inventario_materia_id:
            if inventario_materia and inventario_materia.cantidad >= cantidad:
                inventario_materia.cantidad -= cantidad
                
                inventario_materia.estado_stock = 'bajo' if inventario_materia.cantidad < inventario_materia.cantidad_minima else 'normal'
            else:
                flash('Error: Cantidad insuficiente en inventario de insumos.', 'warning')
                db.session.rollback()
                return redirect(url_for('merma_bp.index'))
        
        if tipo_merma == 'galleta' and inventario_galletas_id:
            if inventario_galletas and inventario_galletas.cantidad >= cantidad:
                inventario_galletas.cantidad -= cantidad
                
                inventario_galletas.estado_stock = 'bajo' if inventario_galletas.cantidad < inventario_galletas.cantidad_minima else 'normal'
            else:
                flash('Error: Cantidad insuficiente en inventario de galletas.', 'warning')
                db.session.rollback()
                return redirect(url_for('merma_bp.index'))
        
        db.session.commit()
        flash('Merma creada correctamente', 'success')
    return redirect(url_for('merma_bp.index'))