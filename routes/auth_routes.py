from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth_forms import LoginForm, RegisterFormLandingPage
from models.models import db, Usuario, Role
from sqlalchemy.exc import IntegrityError
from functools import wraps

auth_bp = Blueprint('auth_bp', _name_, url_prefix='/auth')

# Decorador para requerir login como Cliente
def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for('auth_bp.login'))
        
        user = Usuario.query.get(user_id)
        if not user or user.rol.role_name != "cliente":
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for('auth_bp.login'))
        
        return f(*args, **kwargs)
    return decorated_function


# Cerrar sesión
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('cliente_bp.index'))


# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = Usuario.query.filter_by(correo=email).first()

        if user and check_password_hash(user.contrasenia, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.correo
            session['rol'] = user.rol.role_name
            
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('cliente_bp.index'))
        else:
            flash('Correo electrónico o contraseña incorrectos. Intenta de nuevo.', 'danger')
    return render_template('auth/login.html', form=form)


# Registro de cliente
@auth_bp.route('/register', methods=['GET', 'POST'])
def register_landing():
    form = RegisterFormLandingPage()

    if form.validate_on_submit():
        nombre = form.nombre.data
        telefono = form.telefono.data
        correo = form.correo.data
        username = form.username.data
        password = generate_password_hash(form.password.data)

        if Usuario.query.filter_by(telefono=telefono).first():
            flash("El número de teléfono ya está registrado. Por favor, utiliza otro.", "danger")
            return render_template('auth/register.html', form=form)

        if Usuario.query.filter_by(correo=correo).first():
            flash("El correo electrónico ya está registrado. Por favor, utiliza otro.", "danger")
            return render_template('auth/register.html', form=form)

        if Usuario.query.filter_by(username=username).first():
            flash("El nombre de usuario ya está en uso. Por favor, elige otro.", "danger")
            return render_template('auth/register.html', form=form)

        rol_cliente = Role.query.filter_by(role_name="Cliente").first()
        if not rol_cliente:
            flash("Error: No se encuentra el rol Cliente. Contacta al administrador.", "danger")
            return render_template('auth/register.html', form=form)

        nuevo_usuario = Usuario(
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            username=username,
            contrasenia=password,
            rol_id=rol_cliente.id
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth_bp.login'))
        except IntegrityError:
            db.session.rollback()
            flash("Ocurrió un error al registrar el usuario. Por favor, intenta nuevamente.", "danger")
            return render_template('auth/register.html', form=form)
    return render_template('auth/register.html', form=form)


# Ruta de perfil protegida para clientes
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required_cliente
def profile():
    return render_template('auth/profile.html')


# Ruta de pedidos protegida para clientes
@auth_bp.route('/orders', methods=['GET', 'POST'])
@login_required_cliente
def orders():
    return render_template('auth/orders.html')


# Ruta para restablecer la contraseña (pública)
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def resetpassword():
    return render_template('auth/resetpassword.html')


# Ruta de dashboard administrador (no protegida en este ejemplo)
@auth_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('auth/dashboard.html')
