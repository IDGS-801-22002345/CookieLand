from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from forms.proveedores_form import ProveedorForm
from models.proveedor_model import Proveedores, db
 
provedor_bp = Blueprint('provedor_bp', __name__, url_prefix='/proveedores')
 
@provedor_bp.route("/proveedores")
def index():
    create_form = ProveedorForm(request.form)
    proveedores = Proveedores.query.all()
    proveedores_ordenados = sorted(proveedores, key=lambda x: x.estatus, reverse=True)
    return render_template("proveedores/index.html", form=create_form, proveedores=proveedores_ordenados)

@provedor_bp.route("/cambiar-estatus/<int:id>", methods=["POST"])
def cambiar_estatus(id):
    data = request.get_json()
    nuevo_estatus = data.get("estatus")
    proveedor = Proveedores.query.get(id)
    if not proveedor:
        return jsonify({"success": False, "message": "Proveedor no encontrado"}), 404
    proveedor.estatus = nuevo_estatus
    db.session.commit()
    return jsonify({"success": True})

@provedor_bp.route("/agregar", methods=['POST'])
def agregar_proveedor():
    create_form = ProveedorForm(request.form)
    if request.method == "POST":
        proveedor = Proveedores(
            nombre=create_form.nombre.data,
            telefono=create_form.telefono.data,
            email=create_form.email.data,
            estatus=create_form.estatus.data
        )
        db.session.add(proveedor)
        db.session.commit()
    else:
        flash("Error al agregar el proveedor", "error")
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
            proveedor.estatus = 0
            db.session.commit()
        else:
            flash("Proveedor no encontrado", "error")
    return redirect(url_for('provedor_bp.index'))
