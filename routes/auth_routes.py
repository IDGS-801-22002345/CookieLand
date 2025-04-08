from flask import Blueprint, render_template, redirect, session, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth_forms import *
from models.models import *
from sqlalchemy.exc import IntegrityError
from utils.decoradores import *
from flask_mail import Message # type: ignore
import random
from datetime import datetime, timedelta  
import pytz
import routes.dashboard_routes as dashboard_routes

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@log_excepciones
@anonymous_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        correo = form.email.data.lower()  
        user = Usuario.query.filter_by(correo=correo).first()

        if user:
            intentos = IntentosFallidos.query.filter_by(correo=correo).first()
            if not intentos:
                intentos = IntentosFallidos(correo=correo)
                db.session.add(intentos)
                db.session.commit()

            if intentos.esta_bloqueado:
                tiempo_restante = intentos.bloqueado_hasta - datetime.now(pytz.timezone("America/Mexico_City"))
                minutos = int(tiempo_restante.total_seconds() // 60)
                flash(f'Cuenta bloqueada por demasiados intentos fallidos. Intente nuevamente en {minutos} minutos.', 'danger')
                return redirect(url_for('auth_bp.login'))  

            if check_password_hash(user.contrasenia, form.password.data):

                if not user.verificado:
                    enviar_codigo_verificacion(user)
                    flash('Tu cuenta aún no está verificada. Te hemos reenviado un nuevo código.', 'warning')
                    return redirect(url_for('auth_bp.verificar_codigo', user_id=user.id))

                if user.estatus == 0:
                    flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
                    return redirect(url_for('auth_bp.login'))

                intentos.resetear_intentos()
                login_user(user)
                # Limpiar carrito anterior
                session.pop('carrito', None)

                # Restaurar carrito del usuario desde CarritoTemporal
                temporal = CarritoTemporal.query.filter_by(usuario_id=user.id).all()
                session['carrito'] = []

                for item in temporal:
                    galleta = Galleta.query.get(item.galleta_id)
                    if galleta:
                        presentacion = item.presentacion
                        cantidad = item.cantidad

                        if presentacion == 'caja':
                            piezas = cantidad * 30
                            precio = galleta.precio * 30
                        elif presentacion == 'kilo':
                            piezas = cantidad * 24
                            precio = galleta.precio * 24
                        else:
                            piezas = cantidad
                            precio = galleta.precio

                        session['carrito'].append({
                            'galleta_id': galleta.id,
                            'nombre': galleta.nombre,
                            'precio': precio,
                            'presentacion': presentacion,
                            'cantidad': cantidad,
                            'piezas': piezas
                        })
                user.last_login = datetime.now(pytz.timezone("America/Mexico_City"))
                db.session.commit()

                flash('¡Inicio de sesión exitoso!', 'success')

                if user.has_role('admin'):
                    return redirect(url_for('dashboard_bp.index'))

                elif user.has_role('vendedor'):
                    return redirect(url_for('ventas_bp.index'))

                elif user.has_role('produccion'):
                    return redirect(url_for('produccion_bp.index'))

                else:
                    return redirect(url_for('cliente_bp.index'))
            else:
                intentos.incrementar_intento()
                
                if intentos.intentos >= 3:
                    flash('USUARIO BLOQUEADO: Demasiados intentos fallidos. Cuenta bloqueada por 10 minutos.', 'danger')
                else:
                    intentos_restantes = 3 - intentos.intentos
                    flash(f'Contraseña incorrecta. Te quedan {intentos_restantes} intento(s).', 'warning')

        else:
            flash('El correo no está registrado. Por favor, regístrate o verifica tu correo.', 'danger')
    session.pop('carrito', None)

    return render_template('auth/login.html', form=form)

# Cerrar sesion 
@auth_bp.route('/logout')
@log_excepciones
@login_required
def logout():
    logout_user()
    session.pop('carrito', None)  # Limpia el carrito al cerrar sesión
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('auth_bp.login'))


# Registrar usuario (solamente cliente)
@auth_bp.route('/mk_register', methods=['GET', 'POST'])
@log_excepciones
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
            verificado=False,
            contrasenia=generate_password_hash(form.password.data),
            rol_id=rol_cliente.id
        )
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            enviar_codigo_verificacion(nuevo_usuario)
            flash('Revisa tu correo y confirma tu cuenta con el código de verificación.', 'info')
            return redirect(url_for('auth_bp.verificar_codigo', user_id=nuevo_usuario.id))
        except IntegrityError:
            db.session.rollback()
            flash("Error al registrar usuario.", "danger")
    elif request.method == 'POST':
        flash('Hay errores en el formulario. Por favor verifica los campos.', 'danger')
    return render_template('auth/register.html', form=form)


# Funcion para generar codigo de verificacion (6 digitos)
def generar_codigo():
    return ''.join(random.choices('0123456789', k=6))


# Funcion para enviar correo de verificacion
def enviar_codigo_verificacion(usuario):
    from app import mail
    codigo = generar_codigo()
    expiracion = datetime.utcnow() + timedelta(minutes=5)

    CodigoVerificacion.query.filter_by(usuario_id=usuario.id, verificado=False).delete()
    nuevo_codigo = CodigoVerificacion(
        codigo=codigo,
        usuario_id=usuario.id,
        expiracion=expiracion
    )
    db.session.add(nuevo_codigo)
    db.session.commit()

    msg = Message('Código de verificación', recipients=[usuario.correo])
    msg.html = render_template('email/correo_verificacion.html', usuario=usuario, codigo=codigo)
    mail.send(msg)


# Verificar codigo
@auth_bp.route('/verificar/<int:user_id>', methods=['GET', 'POST'])
@log_excepciones
def verificar_codigo(user_id):
    form = CodigoVerificacionForm()
    usuario = Usuario.query.get_or_404(user_id)
    if form.validate_on_submit():
        codigo = form.codigo.data
        verificacion = CodigoVerificacion.query.filter_by(
            usuario_id=usuario.id, codigo=codigo, verificado=False).first()
        if verificacion:
            if datetime.utcnow() <= verificacion.expiracion:
                verificacion.verificado = True
                usuario.verificado = True
                db.session.commit()

                enviar_correo_verificado(usuario)

                flash("Cuenta verificada exitosamente. Ya puedes iniciar sesión.", "success")
                return redirect(url_for('auth_bp.login'))
            else:
                flash("El código ha expirado. Solicita uno nuevo.", "danger")
        else:
            flash("Código inválido o ya utilizado.", "danger")
    return render_template('auth/verificar_codigo.html', form=form, user_id=user_id)


# Funcion para enviar correo de verificacion exitosa
def enviar_correo_verificado(usuario):
    from app import mail
    msg = Message('¡Tu cuenta ha sido verificada!', recipients=[usuario.correo])
    msg.html = render_template('email/correo_verificado.html', usuario=usuario)
    mail.send(msg)


# Reenviar codigo de verificacion 
@auth_bp.route('/reenviar_codigo/<int:user_id>')
@log_excepciones
def reenviar_codigo(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    if usuario.verificado:
        flash('Tu cuenta ya está verificada.', 'info')
        return redirect(url_for('auth_bp.login'))
    enviar_codigo_verificacion(usuario)
    flash('Se ha enviado un nuevo código de verificación a tu correo.', 'success')
    return redirect(url_for('auth_bp.verificar_codigo', user_id=usuario.id))


# Datos personales del cliente
@auth_bp.route('/mk_profile')
@log_excepciones
@role_required('cliente')
def profile():
    return render_template('auth/profile.html')


# Pedidos del cliente
@auth_bp.route('/mk_orders')
@log_excepciones
@role_required('cliente')
def orders():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('auth/orders.html', pedidos=pedidos)



# Restablecer contraseña
@auth_bp.route('/mk_reset_password')
@log_excepciones
def resetpassword():
    return render_template('auth/resetpassword.html')
