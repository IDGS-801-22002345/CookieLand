from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

class RegistroUsuarioForm(FlaskForm):
    id = HiddenField('ID')

    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=40, message="Debe tener entre 2 y 40 caracteres"),
        Regexp(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ\s]+$', message="Solo letras y espacios")
    ])

    telefono = StringField('Teléfono', validators=[
        DataRequired(message="El teléfono es obligatorio"),
        Regexp(r'^\d{10}$', message="Debe ser un número de 10 dígitos")
    ])

    correo = StringField('Correo', validators=[
        DataRequired(message="Correo obligatorio"),
        Email(message="Correo inválido"),
        Length(max=100)
    ])

    username = StringField('Usuario', validators=[
        DataRequired(),
        Length(min=4, max=15),
        Regexp(r'^[A-Za-z0-9_]+$', message="Solo letras, números y guiones bajos")
    ])

    contrasenia = PasswordField('Contraseña', validators=[
        Optional(),
        Length(min=6, max=20, message="Debe tener entre 6 y 20 caracteres"),
        Regexp(r'^[A-Za-z0-9!@#$%^&*()_+]+$', message="No uses caracteres especiales inválidos")
    ])

    estatus = SelectField('Estatus', choices=[
        ('', 'Opcional'),
        ('1', 'Activo'),
        ('0', 'Inactivo')
    ], validators=[Optional()])

    rol = SelectField('Rol', choices=[
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('produccion', 'Producción')
    ], validators=[DataRequired()])
