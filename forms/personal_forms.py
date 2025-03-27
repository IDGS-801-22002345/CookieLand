from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from wtforms import *

class RegistroUsuarioForm(FlaskForm):
    
    id = HiddenField('ID')

    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(min=2, max=15),
        Regexp(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ\s]+$', message="Solo letras y espacios")
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message="Debe ser un número de 10 dígitos")
    ])
    correo = StringField('Correo', validators=[
        DataRequired(),
        Email(),
        Length(max=100)
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=10),
        Regexp(r'^[A-Za-z0-9_]+$', message="Solo letras, números y guiones bajos")
    ])
    contrasenia = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, max=20)
    ])
    estatus = IntegerField('estatus', [
        DataRequired(message='El estatus es requerido'),
        NumberRange(min=0, max=1, message='El estatus debe ser 0 o 1')
    ])
    rol = SelectField('Rol', choices=[
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('produccion', 'Producción')
    ], validators=[DataRequired()])