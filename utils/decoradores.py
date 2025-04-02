from functools import wraps
from flask import redirect, request, url_for, flash
from flask_login import current_user, login_required
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

# Sesion activa
def anonymous_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            flash('Ya tienes una sesión activa.', 'info')
            return redirect(url_for('cliente_bp.index'))
        return f(*args, **kwargs)
    return decorated

# Acceso con varios roles
def role_required(*role_names):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.rol or current_user.rol.role_name.lower() not in [role.lower() for role in role_names]:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for('auth_bp.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# log_excepciones
def log_excepciones(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Error en '{func.__name__}' - {request.url} - {str(e)}")
            raise e  
    return wrapper
