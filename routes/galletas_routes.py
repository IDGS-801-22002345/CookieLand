from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Receta, Galleta, detalle_recetas, MateriaPrima, db
from forms.recetas_forms import RecetaForm

recetas_bp = Blueprint('recetas_bp', __name__, url_prefix='/galletas')

detalles_receta = []

@recetas_bp.route("/", methods=['GET', 'POST'])
def index():
    recetas_con_insumos = db.session.query(
        Receta,
        MateriaPrima.nombre.label('nombre_insumo'),
        detalle_recetas.c.cantidad
    ).join(
        detalle_recetas,
        detalle_recetas.c.recetaId == Receta.id  
    ).join(
        MateriaPrima,
        detalle_recetas.c.insumoId == MateriaPrima.id 
    ).order_by(Receta.id).all()


    recetas_agrupadas = {}
    for receta, nombre_insumo, cantidad in recetas_con_insumos:
        if receta.id not in recetas_agrupadas:
            recetas_agrupadas[receta.id] = {
                'receta': receta,
                'insumos': []
            }
        recetas_agrupadas[receta.id]['insumos'].append({
            'nombre': nombre_insumo,
            'cantidad': cantidad
        })

    form = RecetaForm(request.form)
    global detalles_receta
    materiales = MateriaPrima.query.all()

    if request.method == 'POST' and form.validate():
        if 'agregar' in request.form:
            materia = MateriaPrima.query.get(form.Insumo.data)
            detalle = {
                'materia_prima_id': form.Insumo.data,
                'nombre': materia.nombre,
                'cantidad': form.Cantidad.data
            }
            detalles_receta.append(detalle)

            form.Insumo.data = ''
            form.NombreInsumo.data = ''
            form.Cantidad.data = 1

    return render_template(
        'galletas/recetas.html',
        form=form,
        detalles=detalles_receta,
        materiales=materiales,
        recetas=list(recetas_agrupadas.values()) 
    )

@recetas_bp.route('/guardar_receta', methods=['POST'])
def guardar_receta():
    nombre_receta = request.form.get('nombre')
    estatus_receta = request.form.get('estatus', 1, type=int)  # Valor por defecto 1
    insumos_ids = request.form.getlist('insumos_seleccionados[]')
    cantidades = request.form.getlist('cantidades_seleccionadas[]')

    # Validaciones
    if not nombre_receta:
        flash("El nombre de la receta es obligatorio.", "error")
        return redirect(url_for('recetas_bp.index'))

    if not insumos_ids or len(insumos_ids) == 0:
        flash("Debes agregar al menos un insumo.", "error")
        return redirect(url_for('recetas_bp.index'))

    # Crear nueva receta con estatus
    nueva_receta = Receta(nombre=nombre_receta, estatus=estatus_receta)
    db.session.add(nueva_receta)
    db.session.commit()

    # Crear galleta asociada
    nueva_galleta = Galleta(nombre=nombre_receta, receta_id=nueva_receta.id)
    db.session.add(nueva_galleta)
    db.session.commit()

    # Agregar insumos a la receta
    for materia_prima_id, cantidad in zip(insumos_ids, cantidades):
        stmt = detalle_recetas.insert().values(
            recetaId=nueva_receta.id,  
            insumoId=int(materia_prima_id), 
            cantidad=int(cantidad)
        )
        db.session.execute(stmt)

    try:
        db.session.commit()
        flash("Receta y galleta creadas correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar la receta: {str(e)}", "error")

    return redirect(url_for('recetas_bp.index'))

@recetas_bp.route('/editar/<int:receta_id>', methods=['GET'])
def editar_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    
    # Obtener insumos actuales
    insumos_actuales = db.session.query(
        MateriaPrima.id,
        MateriaPrima.nombre,
        detalle_recetas.c.cantidad
    ).join(
        detalle_recetas,
        detalle_recetas.c.insumoId == MateriaPrima.id
    ).filter(
        detalle_recetas.c.recetaId == receta_id
    ).all()
    
    # Preparar datos para el template
    detalles_actuales = [{
        'materia_prima_id': insumo.id,
        'nombre': insumo.nombre,
        'cantidad': cantidad
    } for insumo, cantidad in insumos_actuales]
    
    # Crear formulario
    form = RecetaForm(obj=receta)
    form.estatus.data = receta.estatus
    
    materiales = MateriaPrima.query.all()
    opciones_insumos = [(m.id, m.nombre) for m in materiales]
    
    for item in form.insumos:
        item.insumo.choices = opciones_insumos
    
    return render_template(
        'galletas/editar_receta.html',
        form=form,
        receta=receta,
        detalles=detalles_actuales,
        materiales=materiales
    )

@recetas_bp.route('/actualizar/<int:receta_id>', methods=['POST'])
def actualizar_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    form = RecetaForm(request.form)
    
    # Configurar opciones ANTES de validar
    materiales = MateriaPrima.query.all()
    opciones_insumos = [(m.id, m.nombre) for m in materiales]
    
    for item in form.insumos:
        item.insumo.choices = opciones_insumos
    
    if form.validate():
        try:
            # Tu lógica de actualización aquí
            receta.nombre = form.nombre.data
            receta.estatus = form.estatus.data
            
            # Resto de tu código de actualización...
            
            db.session.commit()
            flash("Receta actualizada correctamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar receta: {str(e)}", "error")
    
    return redirect(url_for('recetas_bp.index'))

@recetas_bp.route('/cambiar-estatus/<int:receta_id>', methods=['POST'])
def cambiar_estatus(receta_id):
    if request.method == 'POST':
        try:
            receta = Receta.query.get_or_404(receta_id)
            
            # El checkbox envía 'on' cuando está marcado, None cuando no
            nuevo_estatus = request.form.get('estatus') == 'on'
            receta.estatus = nuevo_estatus
            
            db.session.commit()
            flash('Estatus actualizado correctamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estatus: {str(e)}', 'error')
    
    return redirect(url_for('recetas_bp.index'))