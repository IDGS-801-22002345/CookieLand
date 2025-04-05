from sqlite3 import IntegrityError
from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash
from models.models import Receta, Galleta, MateriaPrima, DetalleReceta, Produccion
from forms.galletas_forms import GalletasForm, InsumosForm, GalletasEditForm
from models.models import db
from utils.decoradores import *


galletas_bp = Blueprint('galletas_bp', __name__, url_prefix='/recetas')

detalles_receta=[]

# Pagina de Recetas

@galletas_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    global detalles_receta
    detalles_receta.clear()
    galletasForm = GalletasForm()
    galletas = Galleta.query.options(db.joinedload(Galleta.receta)).all()
    return render_template("recetas/recetas.html", galletas = galletas, form=galletasForm)

@galletas_bp.route('/imagen/<int:galleta_id>')
@login_required
@log_excepciones
@role_required('admin')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')  

# Pagina para formulario de agregar receta

@galletas_bp.route("/receta-galleta")
@login_required
@log_excepciones
@role_required('admin')
def form():
    global detalles_receta
    galletasForm = GalletasForm()
    insumosForm= InsumosForm()
    return render_template("recetas/formGalletas.html", galletasForm=galletasForm, insumosForm=insumosForm, detalles_receta = detalles_receta)


@galletas_bp.route("/add_insumos", methods=["POST"])
@registrar_accion("Agrego insumos")
@login_required
@log_excepciones
@role_required('admin')
def add_insumos():
    global detalles_receta
    insumosForm = InsumosForm(request.form)
    if request.method == 'POST' and insumosForm.validate():
        insumo_id = insumosForm.insumo.data
        cantidad = insumosForm.cantidad.data
        
        insumo_existente = None
        for item in detalles_receta:
            if item['id'] == insumo_id:
                insumo_existente = item
                break
        
        if insumo_existente:
            insumo_existente['cantidad'] += cantidad
            mensaje = 'Cantidad actualizada correctamente'
        else:
            nombreInsumo = MateriaPrima.query.get(insumo_id).nombre
            unidadInsumo = MateriaPrima.query.get(insumo_id).unidad
            detalles = {
                'id': insumo_id,
                'insumo': nombreInsumo,
                'cantidad': cantidad,
                'unidad': unidadInsumo
            }
            detalles_receta.append(detalles)
            mensaje = 'Material agregado correctamente'
        
        flash(mensaje, 'success')
        return redirect(url_for('galletas_bp.form'))
    
@galletas_bp.route("/eliminar_insumo", methods=["POST"])
@registrar_accion("Elimino insumos")
@login_required
@log_excepciones
@role_required('admin')
def eliminar_insumo():
    global detalles_receta
    insumo_id = request.form.get('insumo_id')
    detalles_receta = [item for item in detalles_receta if str(item['id']) != insumo_id]
    flash('Insumo eliminado de la receta', 'success')
    return redirect(url_for('galletas_bp.form'))
    

@galletas_bp.route("/guardar_receta", methods=["POST"])
@registrar_accion("Guardo receta")
@login_required
@log_excepciones
@role_required('admin')
def guardar_receta():
    global detalles_receta
    print('Entro?')
    galletasForm = GalletasForm(formdata=request.form, **request.files)
    if request.method == 'POST' and galletasForm.validate():
        try:
            if not detalles_receta:
                flash('Debe agregar al menos un ingrediente', 'warning')
                return redirect(url_for('galletas_bp.form'))
            
            nombre_receta = f"Receta de {galletasForm.nombre.data}"
            nueva_receta = Receta(nombre=nombre_receta)
            db.session.add(nueva_receta)
            db.session.flush()
            
            for detalle in detalles_receta:
                nuevo_detalle = DetalleReceta(
                    receta_id=nueva_receta.id,
                    insumo_id=detalle['id'],
                    cantidad=detalle['cantidad']
                )
                db.session.add(nuevo_detalle)
            
            foto_binaria = None
            
            if galletasForm.foto.data:
                foto_binaria = galletasForm.foto.data.read()
            
            nueva_galleta = Galleta(
                nombre=galletasForm.nombre.data,
                receta_id=nueva_receta.id,
                foto=foto_binaria,
            )
            db.session.add(nueva_galleta)
            
            db.session.flush()  
            nueva_produccion = Produccion(
            galleta_id=nueva_galleta.id,
            stock=0,
            estadoStock='Agotado',
            estadoProduccion='Listo',)
            db.session.add(nueva_produccion)
        
            db.session.commit()
            detalles_receta = []
            
            flash('Receta guardada exitosamente!', 'success')
            return redirect(url_for('galletas_bp.index'))
            
        except IntegrityError:
            db.session.rollback()
            flash('El nombre de la galleta ya existe', 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'warning')
        
    return redirect(url_for('galletas_bp.form'))


# ------------Pagina para formulario de editar receta---------------

@galletas_bp.route("/form_edit", methods=["GET", "POST"])
@registrar_accion("Edito insumo")
@login_required
@log_excepciones
@role_required('admin') 
def form_edit():
    global detalles_receta
    galleta_id = request.args.get('galleta_id') if request.method == 'GET' else request.form.get('galleta_id')
    if not galleta_id:
        flash('No se especificó la galleta a editar', 'error')
        return redirect(url_for('galletas_bp.index'))

    galleta = Galleta.query.options(
        db.joinedload(Galleta.receta).joinedload(Receta.detalles).joinedload(DetalleReceta.insumo)
    ).get_or_404(galleta_id)
    
    if not detalles_receta:
        detalles_receta = [{
            'id': detalle.insumo_id,
            'insumo': detalle.insumo.nombre,
            'cantidad': detalle.cantidad,
            'unidad': detalle.insumo.unidad
        } for detalle in galleta.receta.detalles]
    
    galletasForm = GalletasEditForm(nombre=galleta.nombre)
    insumosForm = InsumosForm()
    
    return render_template("recetas/formGalletas.html",
                         galletasForm=galletasForm,
                         insumosForm=insumosForm,
                         detalles_receta=detalles_receta,
                         editar=True,
                         galleta=galleta)

   

@galletas_bp.route("/edit_insumos", methods=["POST"])
@registrar_accion("Edito insumos")
@login_required
@log_excepciones
@role_required('admin')
def edit_insumos():
    global detalles_receta
    insumosForm = InsumosForm(request.form)
    
    if insumosForm.validate():
        galleta_id = request.form.get('galleta_id') 
        insumo_id = insumosForm.insumo.data
        cantidad = insumosForm.cantidad.data
        
        insumo_existente = next((i for i in detalles_receta if i['id'] == insumo_id), None)
        
        if insumo_existente:
            insumo_existente['cantidad'] += cantidad
            flash('Cantidad actualizada', 'success')
        else:
            materia = MateriaPrima.query.get_or_404(insumo_id)
            detalles_receta.append({
                'id': insumo_id,
                'insumo': materia.nombre,
                'cantidad': cantidad,
                'unidad': materia.unidad
            })
            flash('Ingrediente agregado', 'success')
        
        if galleta_id:
            return redirect(url_for('galletas_bp.form_edit', galleta_id=galleta_id))
        return redirect(url_for('galletas_bp.form_edit'))
    
    flash('Error en el formulario', 'warning')
    return redirect(url_for('galletas_bp.index'))

@galletas_bp.route("/edit_eliminar_insumo", methods=["POST"])
@registrar_accion("Elimino insumo")
@login_required
@log_excepciones
@role_required('admin')
def edit_eliminar_insumo():
    galleta_id = request.form.get('galleta_id') 
    global detalles_receta
    insumo_id = request.form.get('insumo_id')
    detalles_receta = [item for item in detalles_receta if str(item['id']) != insumo_id]
    flash('Insumo eliminado de la receta', 'success')
    return redirect(url_for('galletas_bp.form_edit', galleta_id=galleta_id))
    
    
@galletas_bp.route("/editar_receta", methods=["POST"])
@registrar_accion("Edito receta")
@login_required
@log_excepciones
@role_required('admin')
def editar_receta():
    global detalles_receta
    galleta_id = request.form.get('galleta_id')
    
    if not galleta_id:
        flash('No se especificó la galleta a editar', 'error')
        return redirect(url_for('galletas_bp.index'))

    galletasForm = GalletasEditForm(formdata=request.form, **request.files)
    
    if not galletasForm.validate():
        flash('Corrija los errores en el formulario', 'warning')
        return redirect(url_for('galletas_bp.form_edit', galleta_id=galleta_id))

    try:
        if not detalles_receta:
            flash('Debe agregar al menos un ingrediente', 'warning')
            return redirect(url_for('galletas_bp.form_edit', galleta_id=galleta_id))

        galleta = Galleta.query.get_or_404(galleta_id)
        receta = galleta.receta

        galleta.nombre = galletasForm.nombre.data
        receta.nombre = f"Receta de {galletasForm.nombre.data}"

        if galletasForm.foto.data:
            galleta.foto = galletasForm.foto.data.read()

        DetalleReceta.query.filter_by(receta_id=receta.id).delete()
        
        for detalle in detalles_receta:
            db.session.add(DetalleReceta(
                receta_id=receta.id,
                insumo_id=detalle['id'],
                cantidad=detalle['cantidad']
            ))

        db.session.commit()
        detalles_receta = [] 
        
        flash('Receta actualizada exitosamente!', 'success')
        return redirect(url_for('galletas_bp.index'))
        
    except IntegrityError:
        db.session.rollback()
        flash('El nombre de la galleta ya existe', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'warning')
    
    return redirect(url_for('galletas_bp.form_edit', galleta_id=galleta_id))