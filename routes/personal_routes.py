from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from werkzeug.security import generate_password_hash
from forms.personal_forms import RegistroUsuarioForm
from models.models import *
from flask import Blueprint
from utils.decoradores import *

personal_bp = Blueprint('personal_bp', __name__, url_prefix='/')

# Registro de personal interno y (tambien clientes)
@personal_bp.route('/usuarios', methods=['GET', 'POST'])
@log_excepciones
@login_required
@role_required('admin')
def usuarios():
    form = RegistroUsuarioForm()

    usuarios = Usuario.query.all()

    if form.validate_on_submit():
        if Usuario.query.filter_by(correo=form.correo.data).first():
            flash("Este correo ya está registrado.", "danger")
            return render_template('personal/usuarios.html', form=form, usuarios=usuarios)

        if Usuario.query.filter_by(username=form.username.data).first():
            flash("Este nombre de usuario ya está registrado.", "danger")
            return render_template('personal/usuarios.html', form=form, usuarios=usuarios)

        rol = Role.query.filter_by(role_name=form.rol.data).first()
        if not rol:
            flash("Rol no encontrado. Contacta al administrador.", "danger")
            return render_template('personal/usuarios.html', form=form, usuarios=usuarios)

        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            correo=form.correo.data,
            username=form.username,
            estatus=1,
            verificado=True,
            contrasenia=generate_password_hash(form.contrasenia.data),
            rol_id=rol.id 
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("¡Usuario registrado exitosamente!", "success")
            return redirect(url_for('personal_bp.usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar usuario: {e}", "danger")
        
    elif request.method == 'POST':
        flash('Hay errores en el formulario. Por favor verifica los campos.', 'danger')
        
    return render_template('personal/usuarios.html', form=form, usuarios=usuarios)


# Ruta para modificar un usuario
@personal_bp.route('/modificar_usuario', methods=["GET", "POST"])
@log_excepciones
@login_required
@role_required('admin')
def modificar_usuario():
    form = RegistroUsuarioForm(request.form)

    if request.method == "GET":
        id = request.args.get('id')
        usuario = db.session.query(Usuario).filter(Usuario.id == id).first()
        if usuario:
            form.id.data = usuario.id
            form.nombre.data = usuario.nombre
            form.username.data = usuario.username
            form.correo.data = usuario.correo
            form.telefono.data = usuario.telefono
            form.rol.data = usuario.rol.role_name
            form.estatus.data = usuario.estatus
        else:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('personal_bp.usuarios'))

    elif request.method == "POST":
        id = form.id.data
        usuario = db.session.query(Usuario).filter(Usuario.id == id).first()
        if usuario:
            usuario.nombre = form.nombre.data
            usuario.username = form.username.data
            usuario.correo = form.correo.data
            usuario.telefono = form.telefono.data
            usuario.rol_id = Role.query.filter_by(role_name=form.rol.data).first().id
            usuario.estatus = form.estatus.data
            if form.contrasenia.data:
                usuario.contrasenia = generate_password_hash(form.contrasenia.data)
            db.session.commit()
            flash("Usuario actualizado correctamente", "success")
        else:
            flash("Usuario no encontrado", "error")
        return redirect(url_for('personal_bp.usuarios'))

    usuarios = Usuario.query.all()
    return render_template("personal/usuarios.html", form=form, usuarios=usuarios, modificar_modal=True)


# Ruta para eliminar un usuario
@personal_bp.route('/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@log_excepciones
@login_required
@role_required('admin')
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    try:
        usuario.estatus = 0  
        db.session.commit()
        flash(f"Usuario '{usuario.username}' desactivado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo desactivar el usuario: {e}", "danger")

    return redirect(url_for('personal_bp.usuarios'))


# Ruta para la ventana de ventas
@personal_bp.route('/ventas')
@log_excepciones
@role_required('admin')
@login_required
def ventas():
    return render_template('personal/ventas.html')

# Ruta para del layout
@personal_bp.route('/layout')
@log_excepciones
@login_required
def layout():
    return render_template('personal/layout.html')