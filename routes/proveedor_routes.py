from flask import Blueprint, render_template, request, redirect, url_for, flash
from forms.proveedores_form import ProveedorForm
from models.models import Proveedores, db
 
provedor_bp = Blueprint('provedor_bp', __name__, url_prefix='/proveedores')
 
@provedor_bp.route("/proveedores")
def index():
    create_form = ProveedorForm(request.form)
    proveedores = Proveedores.query.all()
    proveedores_ordenados = sorted(proveedores, key=lambda x: x.estatus, reverse=True)
    return render_template("proveedores/index.html", form=create_form, proveedores=proveedores_ordenados)

@provedor_bp.route("/cambiar-estatus", methods=["POST"])
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

@provedor_bp.route("/agregar", methods=['POST'])
def agregar_proveedor():
    form = ProveedorForm(request.form)
    if form.validate():
        try:
            proveedor = Proveedores(
                nombre=form.nombre.data,
                telefono=form.telefono.data,
                email=form.email.data,
                estatus=1  # Siempre activo al crear
            )
            db.session.add(proveedor)
            db.session.commit()
            flash("Proveedor agregado correctamente", "success")
            return redirect(url_for('provedor_bp.index'))
        except Exception as e:
            flash(f"Error al agregar proveedor: {str(e)}", "error")
    else:
        # Si hay errores de validación, mantén el modal abierto
        proveedores = Proveedores.query.all()
        return render_template("proveedores/index.html", 
                            form=form,
                            proveedores=proveedores,
                            mostrar_modal=True)

    return redirect(url_for('provedor_bp.index'))

@provedor_bp.route('/modificar', methods=["GET", "POST"])
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
            proveedor.nombre = create_form.nombre.data
            proveedor.telefono = create_form.telefono.data
            proveedor.email = create_form.email.data
            proveedor.estatus = 1  # Reactivar el proveedor al actualizar
            flash("Proveedor Actualizado correctamente", "success")
            db.session.commit()
        else:
            flash("Proveedor no encontrado", "error")
        return redirect(url_for('provedor_bp.index'))

    proveedores = Proveedores.query.all()
    return render_template("proveedores/index.html", form=create_form, proveedores=proveedores, modificar_modal=True)

 

@provedor_bp.route("/eliminar", methods=["GET", "POST"])
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
