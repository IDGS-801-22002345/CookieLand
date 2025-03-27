from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth_forms import *
from models.models import *
from sqlalchemy.exc import IntegrityError
from utils.decoradores import *

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Usuario.query.filter_by(correo=form.email.data).first()

        if user and check_password_hash(user.contrasenia, form.password.data):
            if user.estatus == 0:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
                return redirect(url_for('auth_bp.login'))

            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')

            if user.has_role('admin'):
                return redirect(url_for('inventario_bp.index'))
            elif user.has_role('cliente'):
                return redirect(url_for('cliente_bp.index'))

        else:
            flash('Las credenciales son incorrectas', 'danger')

    return render_template('auth/login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('cliente_bp.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register_landing():
    form = RegisterFormLandingPage()
    if form.validate_on_submit():
        if Usuario.query.filter_by(correo=form.correo.data).first():
            flash("Este correo ya está registrado.", "danger")
            return render_template('auth/register.html', form=form)

        rol_cliente = Role.query.filter_by(role_name="Cliente").first()
        if not rol_cliente:
            flash("Rol 'Cliente' no encontrado. Contacta al administrador.", "danger")
            return render_template('auth/register.html', form=form)

        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            correo=form.correo.data,
            username=form.username.data,
            estatus=1,
            contrasenia=generate_password_hash(form.password.data),
            rol_id=rol_cliente.id
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth_bp.login'))
        except IntegrityError:
            db.session.rollback()
            flash("Error al registrar usuario.", "danger")
            
    elif request.method == 'POST':
        flash('Hay errores en el formulario. Por favor verifica los campos.', 'danger')
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/profile')
@role_required('cliente')
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/orders')
@role_required('cliente')
def orders():
    return render_template('auth/orders.html')


@auth_bp.route('/reset_password')
def resetpassword():
    return render_template('auth/resetpassword.html')


@auth_bp.route('/dashboard')
def dashboard():
    return render_template('auth/dashboard.html')
