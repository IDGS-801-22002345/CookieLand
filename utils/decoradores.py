from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required

def anonymous_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            flash('Ya tienes una sesión activa.', 'info')
            return redirect(url_for('cliente_bp.index'))
        return f(*args, **kwargs)
    return decorated

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.has_role(role_name):
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for('auth_bp.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
