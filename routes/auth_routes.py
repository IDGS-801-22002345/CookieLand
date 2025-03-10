from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# Ruta para login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Aquí agregarás la lógica de autenticación
        return redirect(url_for('cliente_bp.index'))  # Redirige a la landing page si es exitoso
    return render_template('auth/login.html')

# Ruta para registrar un cliente
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')

# Ruta para restablecer la contraseña
@auth_bp.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    return render_template('auth/resetpassword.html')