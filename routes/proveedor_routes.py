from flask import Blueprint, render_template, request, redirect, url_for, flash
from forms.proveedores_form import ProveedorForm
from models.models import Proveedores, db
from flask_login import login_required
 
from utils.decoradores import *
provedor_bp = Blueprint('provedor_bp', __name__, url_prefix='/')
 
@provedor_bp.route("/mk_proveedores")
@login_required
@log_excepciones
@role_required('admin')

 
def index():
    create_form = ProveedorForm(request.form)
    proveedores = Proveedores.query.all()
    proveedores_ordenados = sorted(proveedores, key=lambda x: x.estatus, reverse=True)
    return render_template("proveedores/index.html", form=create_form, proveedores=proveedores_ordenados)
 
@provedor_bp.route("/mk_cambiar-estatus", methods=["POST"])
@registrar_accion("Cambio estatus proveedor")
@login_required
@log_excepciones
@role_required('admin')
def cambiar_estatus():
    proveedor_id = request.form.get("id")
    proveedor = Proveedores.query.get(proveedor_id)
 
    if not proveedor:
        flash("Proveedor no encontrado", "error")
        return redirect(url_for("provedor_bp.index"))
 
    nuevo_estatus = int(request.form.get("estatus", proveedor.estatus))
    proveedor.estatus = nuevo_estatus
    db.session.commit()
 
    # Alerta agregada para cambio de estatus
    if nuevo_estatus == 1:
        flash("¡Proveedor activado correctamente!", "success")
    else:
        flash("¡Proveedor desactivado correctamente!", "warning")
    return redirect(url_for("provedor_bp.index"))
 
 
@provedor_bp.route("/mk_agregar-proveedor", methods=['POST'])
@registrar_accion("Agrego proveedor")
@login_required
@log_excepciones
@role_required('admin')
def agregar_proveedor():
    form = ProveedorForm(request.form)
   
    if form.validate():
        # Validar duplicados usando una sola consulta para mejor performance
        existente = Proveedores.query.filter(
            (Proveedores.nombre == form.nombre.data) |
            (Proveedores.email == form.email.data) |
            (Proveedores.telefono == form.telefono.data)
        ).first()
 
        if existente:
            if existente.nombre == form.nombre.data:
                flash("Ya existe un proveedor con este nombre.", "error")
            elif existente.email == form.email.data:
                flash("Ya existe un proveedor con este email.", "error")
            elif existente.telefono == form.telefono.data:
                flash("Ya existe un proveedor con este teléfono.", "error")
               
            return render_template("proveedores/index.html",
                                form=form,
                                proveedores=Proveedores.query.all(),
                                mostrar_modal=True,
                                modal_error=True)
 
        try:
            proveedor = Proveedores(
                nombre=form.nombre.data,
                telefono=form.telefono.data,
                email=form.email.data,
                estatus=1
            )
            db.session.add(proveedor)
            db.session.commit()
            flash("Proveedor agregado correctamente", "success")
            return redirect(url_for('provedor_bp.index'))
           
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar proveedor: {str(e)}", "error")
            return render_template("proveedores/index.html",
                                form=form,
                                proveedores=Proveedores.query.all(),
                                mostrar_modal=True,
                                modal_error=True)
   
    # Si hay errores de validación del formulario
 
   
    return render_template("proveedores/index.html",
                         form=form,
                         proveedores=Proveedores.query.all(),
                         mostrar_modal=True,
                         modal_error=True)
 
@provedor_bp.route('/mk_modificar-proveedor', methods=["GET", "POST"])
@registrar_accion("Modifico proveedor")
@login_required
@log_excepciones
@role_required('admin')
def modificar():
    create_form = ProveedorForm(request.form)
   
    if request.method == "GET":
        id = request.args.get('id')
        proveedor = db.session.query(Proveedores).filter(Proveedores.id == id).first()
        if proveedor:
            create_form.id.data = id
            create_form.nombre.data = proveedor.nombre
            create_form.telefono.data = proveedor.telefono
            create_form.email.data = proveedor.email
        else:
            flash("Proveedor no encontrado", "error")
            return redirect(url_for('provedor_bp.index'))
   
    elif request.method == "POST":
        id = create_form.id.data
        proveedor = db.session.query(Proveedores).filter(Proveedores.id == id).first()
       
        if proveedor:
            # Validar duplicados excluyendo el proveedor actual
            existente = Proveedores.query.filter(
                (Proveedores.id != id) & (
                    (Proveedores.nombre == create_form.nombre.data) |
                    (Proveedores.email == create_form.email.data) |
                    (Proveedores.telefono == create_form.telefono.data)
                )
               
            ).first()
 
            if existente:
                if existente.nombre == create_form.nombre.data:
                    flash("Ya existe otro proveedor con este nombre.", "error")
                elif existente.email == create_form.email.data:
                    flash("Ya existe otro proveedor con este email.", "error")
                elif existente.telefono == create_form.telefono.data:
                    flash("Ya existe otro proveedor con este teléfono.", "error")
               
                return render_template("proveedores/index.html",
                                    form=create_form,
                                    proveedores=Proveedores.query.all(),
                                    modificar_modal=True,
                                     )
 
            try:
                proveedor.nombre = create_form.nombre.data
                proveedor.telefono = create_form.telefono.data
                proveedor.email = create_form.email.data
                proveedor.estatus = 1  # Reactivar el proveedor al actualizar
               
                db.session.commit()
                flash("Proveedor actualizado correctamente", "success")
                return redirect(url_for('provedor_bp.index'))
               
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar proveedor: {str(e)}", "error")
                return render_template("proveedores/index.html",
                                     form=create_form,
                                     proveedores=Proveedores.query.all(),
                                     modificar_modal=True,
                                     agregar_modal=False,
                                     modal_error=True)
        else:
            flash("Proveedor no encontrado", "error")
            return redirect(url_for('provedor_bp.modificar'))
 
    # Si hay errores de validación del formulario
    for field, errors in create_form.errors.items():
        for error in errors:
            flash(f"{getattr(create_form, field).label.text}: {error}", "error")
   
    return render_template("proveedores/index.html",
                         form=create_form,
                         proveedores=Proveedores.query.all(),
                         modificar_modal=True,
                         modal_error=True)
 
 
@provedor_bp.route("/mk_eliminar", methods=["GET", "POST"])
@registrar_accion("Eliminó un proveedor")
@login_required
@log_excepciones
@role_required('admin')
def eliminar():
    if request.method == "GET":
        id = request.args.get('id')
        proveedor = Proveedores.query.get(id)
        if proveedor:
            try:
                proveedor.estatus = 0
                db.session.commit()
                # Alerta agregada para desactivación exitosa
                flash("¡Proveedor desactivado correctamente!", "warning")
            except Exception as e:
                # Alerta agregada para error en desactivación
                flash(f"Error al desactivar el proveedor: {str(e)}", "error")
        else:
            flash("Proveedor no encontrado", "error")
    return redirect(url_for('provedor_bp.index'))