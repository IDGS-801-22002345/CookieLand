from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Receta, Galleta, detalle_recetas, MateriaPrima, db
from forms.recetas_forms import RecetaForm
from werkzeug.utils import secure_filename
import os
import base64

recetas_bp = Blueprint('recetas_bp', __name__, url_prefix='/galletas')

detalles_receta = []

@recetas_bp.route("/")
def index():
    create_form = RecetaForm(request.form)
    materiales = MateriaPrima.query.all()
    
    recetas = Receta.query.all()
    recetas_data = []
    
    for receta in recetas:
        insumos = db.session.execute(
            detalle_recetas.select().where(detalle_recetas.c.recetaId == receta.id)
        ).fetchall()
        
        insumos_con_nombre = []
        for insumo in insumos:
            materia = MateriaPrima.query.get(insumo.insumoId)
            insumos_con_nombre.append({
                'id': insumo.insumoId,
                'nombre': materia.nombre,
                'cantidad': insumo.cantidad
            })
        
        galleta = Galleta.query.filter_by(receta_id=receta.id).first()
        
        recetas_data.append({
            'receta': receta,
            'insumos': insumos_con_nombre,
            'galleta': galleta
        })
    
    return render_template("galletas/recetas.html", 
                         form=create_form, 
                         recetas=recetas_data,
                         materiales=materiales)

@recetas_bp.route('/guardar_receta', methods=['POST'])
def guardar_receta():
    nombre_receta = request.form.get('nombre')
    foto = request.files.get('foto')
    insumos_ids = request.form.getlist('insumos_seleccionados[]')
    cantidades = request.form.getlist('cantidades_seleccionadas[]')

    if not nombre_receta:
        flash("El nombre es requerido", "error")
        return redirect(url_for('recetas_bp.index'))

    if not foto or foto.filename == '':
        flash("Debes subir una imagen", "error")
        return redirect(url_for('recetas_bp.index'))

    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if '.' not in foto.filename or foto.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        flash("Formato de imagen no válido. Use JPG, PNG o JPEG", "error")
        return redirect(url_for('recetas_bp.index'))

    try:
        foto_data = foto.read()

        nueva_receta = Receta(nombre=nombre_receta, estatus=1)
        db.session.add(nueva_receta)
        db.session.flush() 

        nueva_galleta = Galleta(
            nombre=nombre_receta,
            receta_id=nueva_receta.id,
            foto=foto_data
        )
        db.session.add(nueva_galleta)

        for insumo_id, cantidad in zip(insumos_ids, cantidades):
            stmt = detalle_recetas.insert().values(
                recetaId=nueva_receta.id,
                insumoId=int(insumo_id),
                cantidad=int(cantidad)
            )
            db.session.execute(stmt)

        db.session.commit()
        flash("Receta guardada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar: {str(e)}", "error")

    return redirect(url_for('recetas_bp.index'))

@recetas_bp.route('/actualizar/<int:receta_id>', methods=["GET", "POST"])
def actualizar_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    galleta = Galleta.query.filter_by(receta_id=receta_id).first()
    
    if request.method == "GET":
        insumos = db.session.execute(
            detalle_recetas.select().where(detalle_recetas.c.recetaId == receta_id)
        ).fetchall()
        
        return render_template("modificar_receta.html", 
                            receta=receta,
                            galleta=galleta,
                            insumos=insumos,
                            materiales=MateriaPrima.query.all())  
    
    elif request.method == "POST":
        try:
            receta.nombre = request.form.get('nombre', receta.nombre)
            if galleta:
                galleta.nombre = receta.nombre
            
            if 'nueva_foto' in request.files:
                nueva_foto = request.files['nueva_foto']
                if nueva_foto and nueva_foto.filename != '':
                    if '.' in nueva_foto.filename and \
                       nueva_foto.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}:
                        galleta.foto = nueva_foto.read()
            
                
                for insumo_id, cantidad in request.form.getlist('insumos'):
                    if insumo_id and cantidad:
                        db.session.execute(
                            detalle_recetas.insert().values(
                                recetaId=receta_id,
                                insumoId=int(insumo_id),
                                cantidad=float(cantidad)
                            )
                        )
            
            db.session.commit()
            flash("Receta actualizada correctamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "error")
        
        return redirect(url_for('recetas_bp.index'))

@recetas_bp.route('/cambiar-estatus/<int:receta_id>', methods=['POST'])
def cambiar_estatus(receta_id):
    if request.method == 'POST':
        try:
            receta = Receta.query.get_or_404(receta_id)
            

            nuevo_estatus = request.form.get('estatus') == 'on'
            receta.estatus = nuevo_estatus
            
            db.session.commit()
            flash('Estatus actualizado correctamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estatus: {str(e)}', 'error')
    
    return redirect(url_for('recetas_bp.index'))