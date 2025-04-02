from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length,Email, Regexp
from werkzeug.security import check_password_hash
from models.models import Usuario

# Validadores para login 
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(), Length(min=6)
    ])
    recaptcha = RecaptchaField()  

    def validate_email(self, field):
        user = Usuario.query.filter_by(correo=field.data).first()
        if not user:
            raise ValidationError('El correo electrónico no está registrado.')

    def validate_password(self, field):
        user = Usuario.query.filter_by(correo=self.email.data).first()
        if user and not check_password_hash(user.contrasenia, field.data):
            raise ValidationError('La contraseña es incorrecta.')
    
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