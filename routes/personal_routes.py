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
            username=form.username.data,
            estatus=1,
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


# Ruta para editar un usuario
@personal_bp.route('/modificar_usuario', methods=["GET", "POST"])
@role_required('admin')
def modificar_usuario():
    form = RegistroUsuarioForm(request.form)
    id = form.id.data  

    usuario = Usuario.query.get(id)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('personal_bp.usuarios'))
    
    if request.method == "GET":
        id = request.args.get('id')
        usuario = Usuario.query.get(id)

        if usuario:
            form.id.data = usuario.id
            form.nombre.data = usuario.nombre
            form.username.data = usuario.username
            form.correo.data = usuario.correo
            form.telefono.data = usuario.telefono
            form.rol.data = usuario.rol.role_name if usuario.rol else ''
            form.estatus.data = usuario.estatus
        else:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for('personal_bp.usuarios'))

    elif request.method == "POST":
        id = form.id.data
        usuario = Usuario.query.get(id)

        if usuario:
            # Verifica duplicados excluyendo el mismo usuario
            if Usuario.query.filter(Usuario.correo == form.correo.data, Usuario.id != usuario.id).first():
                flash("Otro usuario ya tiene ese correo.", "danger")
                return redirect(url_for('personal_bp.usuarios'))

            if Usuario.query.filter(Usuario.username == form.username.data, Usuario.id != usuario.id).first():
                flash("Otro usuario ya tiene ese nombre de usuario.", "danger")
                return redirect(url_for('personal_bp.usuarios'))

            rol = Role.query.filter_by(role_name=form.rol.data).first()
            if not rol:
                flash("Rol no válido", "danger")
                return redirect(url_for('personal_bp.usuarios'))

            # Asignación
            usuario.nombre = form.nombre.data
            usuario.username = form.username.data
            usuario.correo = form.correo.data
            usuario.telefono = form.telefono.data
            usuario.rol_id = rol.id
            usuario.estatus = int(form.estatus.data)

            # Nueva contraseña si se envía
            nueva_contrasenia = request.form.get("nueva_contrasenia")
            if nueva_contrasenia and nueva_contrasenia.strip():
                if len(nueva_contrasenia.strip()) < 6:
                    flash("La nueva contraseña debe tener al menos 6 caracteres.", "danger")
                    return redirect(url_for('personal_bp.usuarios'))
                usuario.contrasenia = generate_password_hash(nueva_contrasenia.strip())

            try:
                db.session.commit()
                flash("Usuario actualizado correctamente.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar usuario: {e}", "danger")
        else:
            flash("Usuario no encontrado", "danger")

        return redirect(url_for('personal_bp.usuarios'))

    usuarios = Usuario.query.all()
    return render_template("personal/usuarios.html", form=form, usuarios=usuarios, modificar_modal=True)


# Ruta para eliminar un usuario
@personal_bp.route('/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@role_required('admin')
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f"Usuario '{usuario.username}' eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar el usuario: {e}", "danger")

    return redirect(url_for('personal_bp.usuarios'))

@personal_bp.route('/cargar_usuario', methods=['POST'])
@role_required('admin')
def cargar_usuario():
    form = RegistroUsuarioForm()
    id = request.form.get('id')

    usuario = Usuario.query.get_or_404(id)
    form.id.data = usuario.id
    form.nombre.data = usuario.nombre
    form.username.data = usuario.username
    form.correo.data = usuario.correo
    form.telefono.data = usuario.telefono
    form.rol.data = usuario.rol.role_name if usuario.rol else ''
    form.estatus.data = usuario.estatus

    usuarios = Usuario.query.all()
    return render_template("personal/usuarios.html", form=form, usuarios=usuarios, modificar_modal=True)




# Ruta para la ventana de ventas
@personal_bp.route('/ventas')
def ventas():
    return render_template('personal/ventas.html')

# Ruta para del layout
@personal_bp.route('/layout')
def layout():
    return render_template('personal/layout.html')