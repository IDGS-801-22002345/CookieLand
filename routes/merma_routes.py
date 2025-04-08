from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima
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

    materias = db.session.query(
        MateriaPrima.id, 
        MateriaPrima.nombre, 
        MateriaPrima.unidad
    ).order_by(MateriaPrima.nombre).all()

    create_form.inventario_materia_id.choices = [(m.id, f"{m.nombre}") for m in materias]
    print(f"ID de inventario seleccionado: {InventarioMateria.id}")

    galletas = Galleta.query.order_by(Galleta.nombre).all()
    create_form.galleta_id.choices = [(g.id, g.nombre) for g in galletas]

    mermas = db.session.query(Merma).outerjoin(
        InventarioMateria, Merma.inventario_materia_id == InventarioMateria.id
    ).outerjoin(
        Galleta, Merma.galleta_id == Galleta.id
    ).order_by(Merma.fecha.desc()).all()

    unidades_materias = {m.id: m.unidad for m in materias}

    print("Unidades a enviar al frontend:", unidades_materias)

    items = MateriaPrima.query.all()
    for item in items:
        print(f"ID: {item.id}, Nombre: {item.nombre}, Unidad: {item.unidad}")

    return render_template(
        "merma/merma.html", 
        form=create_form, 
        mermas=mermas,
        unidades_materias=unidades_materias
    )


@merma_bp.route("/obtener_unidad/<int:inventario_id>")
@login_required
def obtener_unidad(inventario_id):
    inventario = InventarioMateria.query.get_or_404(inventario_id)
    return jsonify({'unidad': inventario.materia_prima.unidad if inventario.materia_prima else 'N/A'})

@merma_bp.route("/crear", methods=['POST'])
@registrar_accion("Agrego merma")
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
def crear():
    create_form = MermaForm(request.form)
    
    materias = db.session.query(
        InventarioMateria.id, 
        MateriaPrima.nombre, 
        MateriaPrima.unidad
    ).join(MateriaPrima).all()
    
    create_form.inventario_materia_id.choices = [(m.id, f"{m.nombre} ({m.unidad})") for m in materias]

    print("Opciones de inventario_materia_id:", create_form.inventario_materia_id.choices)

    create_form.galleta_id.choices = [(g.id, g.nombre) for g in Galleta.query.all()]

    if create_form.validate():
        try:
            tipo_merma = create_form.tipo_merma.data
            cantidad = float(create_form.cantidad.data)
            inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
            galleta_id = create_form.galleta_id.data if tipo_merma == 'galleta' else None

            inventario_item = None
            item_nombre = None
            unidad = None

            if tipo_merma == 'galleta' and galleta_id:
                galleta = Galleta.query.get(galleta_id)
                if not galleta:
                    flash('Error: Galleta no encontrada.', 'warning')
                    return redirect(url_for('merma_bp.index'))
                inventario_item = galleta
                item_nombre = galleta.nombre
                unidad = 'pz' 

            elif tipo_merma == 'insumo' and inventario_materia_id:
                inventario_materia = InventarioMateria.query.get(inventario_materia_id)
                
                if not inventario_materia:
                    flash('Error: Inventario de insumos no encontrado.', 'warning')
                    return redirect(url_for('merma_bp.index'))

                inventario_item = inventario_materia
                item_nombre = inventario_materia.materia_prima.nombre if inventario_materia.materia_prima else "Insumo desconocido"
                unidad = inventario_materia.materia_prima.unidad if inventario_materia.materia_prima else 'N/A'

            if not inventario_item:
                flash('Error: Debe seleccionar un insumo o galleta válida.', 'warning')
                return redirect(url_for('merma_bp.index'))

            if cantidad <= 0:
                flash('Error: La cantidad debe ser mayor que cero.', 'warning')
                return redirect(url_for('merma_bp.index'))

            cantidad_actual = getattr(inventario_item, 'cantidad', getattr(inventario_item, 'stock', 0))
            
            print(f"Cantidad solicitada: {cantidad} | Stock actual: {cantidad_actual} | Unidad: {unidad}")
            
            if cantidad_actual < cantidad:
                flash(f'Error: No hay suficiente stock de {item_nombre}. Stock actual: {cantidad_actual} {unidad}', 'warning')
                return redirect(url_for('merma_bp.index'))

            if hasattr(inventario_item, 'cantidad'):
                inventario_item.cantidad -= cantidad
                estado_stock = 'Agotado' if inventario_item.cantidad == 0 else \
                               'Bajo' if inventario_item.cantidad < getattr(inventario_item, 'cantidad_minima', 0) else 'Alto'
                inventario_item.estado_stock = estado_stock
            else:
                inventario_item.stock -= cantidad

            merma = Merma(
                descripcion=create_form.descripcion.data,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                inventario_materia_id=inventario_materia_id,
                galleta_id=galleta_id,
                fecha=datetime.datetime.now()
            )
            
            db.session.add(merma)
            db.session.commit()
            
            flash(f'Merma registrada correctamente: {cantidad} {unidad} de {item_nombre}', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la merma: {str(e)}', 'danger')
            traceback.print_exc()

    else:
        for field, errors in create_form.errors.items():
            for error in errors:
                flash(f'Error en {getattr(create_form, field).label.text}: {error}', 'warning')

    return redirect(url_for('merma_bp.index'))

