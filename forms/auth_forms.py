from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length,Email, Regexp
from werkzeug.security import check_password_hash
from models.models import *
from flask_wtf import RecaptchaField

from datetime import datetime, timedelta

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    recaptcha = RecaptchaField()  

    def validate_email(self, field):
        correo = field.data.lower()
        # Comprobamos si el correo está bloqueado
        intentos = IntentosFallidos.query.filter_by(correo=correo).first()

        if intentos and intentos.esta_bloqueado:
            # Calculamos el tiempo restante para desbloqueo
            tiempo_restante = intentos.bloqueado_hasta - datetime.now(pytz.timezone("America/Mexico_City"))
            minutos = int(tiempo_restante.total_seconds() // 60)
            raise ValidationError(f'Usuario bloqueado. Intente nuevamente en {minutos} minutos.')

        user = Usuario.query.filter_by(correo=correo).first()
        if not user:
            raise ValidationError('El correo electrónico no está registrado.')

    def validate_password(self, field):
        correo = self.email.data.lower()
        intentos = IntentosFallidos.query.filter_by(correo=correo).first()

        # Si no existe el registro de intentos, lo creamos
        if not intentos:
            intentos = IntentosFallidos(correo=correo)
            db.session.add(intentos)
            db.session.commit()

        user = Usuario.query.filter_by(correo=correo).first()

        # Si no se encuentra el usuario o la contraseña es incorrecta
        if not user or not check_password_hash(user.contrasenia, field.data):
            intentos.incrementar_intento()

            if intentos.intentos >= 3:
                raise ValidationError('Usuario bloqueado. Demasiados intentos fallidos.')
            else:
                intentos_restantes = 3 - intentos.intentos
                raise ValidationError(f'Contraseña incorrecta. Intentos restantes: {intentos_restantes}')
        else:
            if intentos.intentos > 0:
                intentos.resetear_intentos()
    
# Validadores para registro cliente (landing page)
class RegisterFormLandingPage(FlaskForm):
    nombre = StringField("Nombre", validators=[
        DataRequired(), Length(min=3, max=50)
    ])
    telefono = StringField("Teléfono", validators=[
        DataRequired(),Length(min=10, max=10),
        Regexp(r'^[0-9]*$', message="El teléfono solo puede contener números.")
    ])
    correo = StringField("Correo", validators=[
        DataRequired(), 
        Email(message="Por favor, ingresa un correo electrónico válido.")
    ])
    username = StringField("Usuario", validators=[
        DataRequired(), Length(min=4, max=10)
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired(),Length(min=6, max=12),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$', 
        message="La contraseña debe tener al menos 8 caracteres, una letra y un número.")
    ])

# Validadores para codigo de verificacion
class CodigoVerificacionForm(FlaskForm):
    codigo = StringField("Código de Verificación", validators=[
        DataRequired(message="Este campo es obligatorio."),
        Length(min=6, max=6, message="El código debe tener 6 dígitos.")
    ])